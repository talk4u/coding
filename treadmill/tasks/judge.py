from contextlib import ExitStack
import filecmp

from treadmill.signal import SubmissionCompileError, GraderCompileError

from .base import SimpleTask
from .container import *
from .workspace import *


__all__ = [

]


class JudgeAllTask(SimpleTask):
    def _run_impl(self):
        with ExitStack() as stack:
            subm_sandbox = SandboxContainerContext(
                lang=self.context.subm_lang,
                isolated=True
            )
            stack.enter_context(subm_sandbox.run(self.context))
            if self.context.grader is not None:
                grader_sandbox = SandboxContainerContext(
                    lang=self.context.grader_lang,
                    isolated=False
                )
                stack.enter_context(grader_sandbox.run(self.context))
            else:
                grader_sandbox = None

            for testset in self.context.judge_spec.testsets:
                testset_result = JudgeTestSetTask(
                    subm_sandbox=subm_sandbox,
                    grader_sandbox=grader_sandbox,
                    testset=testset
                ).run(self.context)


class JudgeTestSetTask(SimpleTask):
    def __init__(self, subm_sandbox, grader_sandbox, testset):
        self._subm_sandbox: SandboxContainerContext = subm_sandbox
        self._grader_sandbox: SandboxContainerContext = grader_sandbox
        self.testset = testset

    def _run_impl(self):
        for testcase in self.testset.cases:
            input_file = self._test_input_file(self.testset, testcase)
            expected_file = self._host_path(self._test_output_file(self.testset, testcase))

            result = ExecuteTask(
                container=self._subm_sandbox,
                stdin_file=input_file,
                bin_file=self._subm_bin_file
            ).run(self.context)

            if self._grader_sandbox:
                result = ExecuteTask(
                    container=self._grader_sandbox,
                    stdin_file=result.stdout_file,
                    bin_file=self._grader_bin_file
                ).run(self.context)

            output_file = self._host_path(result.stdout_file)

            passed = filecmp.cmp(output_file, expected_file, shallow=False)

            if passed:
                self.context.api_client.set_passed(
                    self.context.request.id,
                    self.testset.id,
                    testcase.id
                )
            else:
                self.context.api_client.set_wrong_answer(
                    self.context.request.id,
                    self.testset.id,
                    testcase.id
                )
                break


class CompileAllTask(SimpleTask):
    def _run_impl(self):
        with BuilderContainerContext(lang=self.context.subm_lang) as subm_builder:
            result = CompileTask(
                container=subm_builder,
                src_file=self._subm_src_file,
                bin_file=self._subm_bin_file
            ).run(self.context)

            if result.exit_code != 0:
                raise SubmissionCompileError(result.output)

            if self.context.grader:
                if self.context.grader_lang == self.context.subm_lang:
                    result = CompileTask(
                        container=subm_builder,
                        src_file=self._grader_src_file,
                        bin_file=self._grader_bin_file
                    ).run(self.context)
                else:
                    with BuilderContainerContext(lang=self.context.grader_lang) as grader_builder:
                        result = CompileTask(
                            container=grader_builder,
                            src_file=self._grader_src_file,
                            bin_file=self._grader_bin_file
                        ).run(self.context)

                if result.exit_code != 0:
                    raise GraderCompileError(result.output)


class TreadmillTask(SimpleTask):
    def _run_impl(self):
        self.context.submission = self.context.api_client.get_submission_detail()

        with WorkspaceContext():
            CompileAllTask().run(self.context)
            JudgeAllTask().run(self.context)

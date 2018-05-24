from contextlib import ExitStack

from treadmill.signal import SubmissionCompileError, GraderCompileError

from .base import SimpleTask
from .container import BuildContext, SandboxContext, CompileTask
from .workspace import WorkspaceContext
from .judge import JudgeTestSetTask


__all__ = [
    'CompileAllTask',
    'JudgeAllTask',
    'TreadmillTask'
]


class CompileAllTask(SimpleTask):
    def _run_impl(self):
        with BuildContext(lang=self.context.subm_lang) as subm_builder:
            result = CompileTask(
                builder=subm_builder,
                src_file=self._subm_src_file,
                bin_file=self._subm_bin_file
            ).run(self.context)

            if result.exit_code != 0:
                raise SubmissionCompileError(result.output)

            if self.context.grader:
                if self.context.grader_lang == self.context.subm_lang:
                    result = CompileTask(
                        builder=subm_builder,
                        src_file=self._grader_src_file,
                        bin_file=self._grader_bin_file
                    ).run(self.context)
                else:
                    with BuildContext(lang=self.context.grader_lang) as grader_builder:
                        result = CompileTask(
                            builder=grader_builder,
                            src_file=self._grader_src_file,
                            bin_file=self._grader_bin_file
                        ).run(self.context)

                if result.exit_code != 0:
                    raise GraderCompileError(result.output)


class JudgeAllTask(SimpleTask):
    def _run_impl(self):
        with ExitStack() as stack:
            subm_sandbox = SandboxContext(
                lang=self.context.subm_lang,
                isolated=True
            )
            stack.enter_context(subm_sandbox.run(self.context))
            if self.context.grader is not None:
                grader_sandbox = SandboxContext(
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


class TreadmillTask(SimpleTask):
    def _run_impl(self):
        self.context.submission = self.context.api_client.get_submission_detail()

        with WorkspaceContext():
            CompileAllTask().run(self.context)
            JudgeAllTask().run(self.context)

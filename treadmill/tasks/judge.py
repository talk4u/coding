from contextlib import ExitStack
import filecmp

from treadmill.models import *
from treadmill.signal import *

from .base import SimpleTask
from .container import BuilderContext, SandboxContext, CompileTask, ExecuteTask
from .workspace import WorkspaceContext


class JudgeTestSetTask(SimpleTask):
    def __init__(self, subm_sandbox, grader_sandbox, testset):
        self._subm_sandbox: SandboxContext = subm_sandbox
        self._grader_sandbox: SandboxContext = grader_sandbox
        self.testset = testset
        self.subm_exec_result = None
        self.score = 0

    def _save_testcase_result(self, testcase_id, status,
                              memory_used_bytes=None,
                              time_elapsed_seconds=None,
                              error=None):
        self.context.api_client.set_testcase_judge_result(
            self.context.request.id,
            self.testset.id,
            testcase_id,
            TestCaseJudgeResult(
                status=status,
                memory_used_bytes=memory_used_bytes,
                time_elapsed_seconds=time_elapsed_seconds,
                error=error
            )
        )

    def _save_testset_result(self, passed):
        if passed:
            self.score = self.context.judge_spec.testsets[self.testset.id].score

        self.context.api_client.set_testset_judge_result(
            self.context.request.id,
            self.testset.id,
            TestSetJudgeResult(score=self.score)
        )

    def _run_impl(self):
        for testcase in self.testset.cases:
            try:
                meta = self._judge_testcase(testcase)
                self._save_testcase_result(
                    testcase.id,
                    status=TestCaseJudgeStatus.PASS,
                    memory_used_bytes=meta.max_rss,
                    time_elapsed_seconds=meta.time
                )
                continue
            except ServerFault:
                self._save_testcase_result(
                    testcase.id,
                    status=TestCaseJudgeStatus.NOT_JUDGED
                )
                self._save_testset_result(passed=False)
                raise
            except Timeout:
                self._save_testcase_result(
                    testcase.id,
                    status=TestCaseJudgeStatus.TIME_LIMIT_EXCEEDED,
                )
            except OutOfMemory:
                self._save_testcase_result(
                    testcase.id,
                    status=TestCaseJudgeStatus.MEMORY_LIMIT_EXCEEDED,
                )
            except SubmissionRuntimeError:
                self._save_testcase_result(
                    testcase.id,
                    status=TestCaseJudgeStatus.RUNTIME_ERROR
                )
            except WrongAnswer:
                self._save_testcase_result(
                    testcase.id,
                    status=TestCaseJudgeStatus.WRONG_ANSWER
                )
            return
        self.score = self.context.judge_spec.testsets[self.testset.id].score
        self.context.api_client.set_testset_judge_result(
            self.context.request.id,
            self.testset.id,
            TestSetJudgeResult(score=self.score)
        )

    def _judge_testcase(self, testcase):
        input_file = self._test_input_file(self.testset, testcase)
        expected_file = self.context.host_path(self._test_output_file(self.testset, testcase))

        result = ExecuteTask(
            sandbox=self._subm_sandbox,
            stdin_file=input_file,
            bin_file=self._subm_bin_file
        ).run(self.context)
        subm_exec_meta = result.meta

        if not result.ok:
            if result.is_fatal:
                raise IsolateExecutionError(result.output)
            elif result.is_timeout:
                raise Timeout()
            elif result.is_out_of_memory:
                raise OutOfMemory()
            else:
                raise SubmissionRuntimeError()

        if self._grader_sandbox:
            result = ExecuteTask(
                sandbox=self._grader_sandbox,
                stdin_file=result.stdout_file,
                bin_file=self._grader_bin_file
            ).run(self.context)

            if not result.ok:
                raise GraderRuntimeError(result.stderr)

        output_file = self.context.host_path(result.stdout_file)

        if not filecmp.cmp(output_file, expected_file, shallow=False):
            raise WrongAnswer()

        return subm_exec_meta


class CompileAllSourcesTask(SimpleTask):
    def _run_impl(self):
        with BuilderContext(lang=self.context.subm_lang) as subm_builder:
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
                    with BuilderContext(lang=self.context.grader_lang) as grader_builder:
                        result = CompileTask(
                            builder=grader_builder,
                            src_file=self._grader_src_file,
                            bin_file=self._grader_bin_file
                        ).run(self.context)

                if result.exit_code != 0:
                    raise GraderCompileError(result.output)


class JudgeInSandboxTask(SimpleTask):
    total_score: int

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

            self.total_score = 0
            for testset in self.context.judge_spec.testsets:
                result = JudgeTestSetTask(
                    subm_sandbox=subm_sandbox,
                    grader_sandbox=grader_sandbox,
                    testset=testset
                ).run(self.context)
                self.total_score += result.score


class TreadmillJudgeTask(SimpleTask):
    def set_judge_result(self, *, status, score=None):
        self.context.api_client.set_judge_result(
            self.context.request.id,
            JudgeResult(status=status, score=score)
        )

    def _run_impl(self):
        try:
            self.context.submission = self.context.api_client.get_submission(self.context.request.submission_id)
            self.set_judge_result(status=JudgeStatus.IN_PROGRESS)
            with WorkspaceContext():
                CompileAllSourcesTask().run(self.context)
                result = JudgeInSandboxTask().run(self.context)
                if result.total_score >= self.context.judge_spec.total_score:
                    self.set_judge_result(status=JudgeStatus.PASS, score=result.total_score)
                else:
                    self.set_judge_result(status=JudgeStatus.FAIL, score=result.total_score)
        except SubmissionCompileError:
            self.set_judge_result(status=JudgeStatus.COMPILE_ERROR)
        except ServerFault as e:
            self.set_judge_result(status=JudgeStatus.INTERNAL_ERROR)
            self.context.log_current_error()
            if e.retryable:
                raise
        except TreadmillSignal as e:
            if e.retryable:
                raise
        except Exception:
            self.context.log_current_error()

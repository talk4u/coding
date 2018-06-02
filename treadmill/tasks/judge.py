from contextlib import ExitStack

from treadmill.models import *
from treadmill.signal import *
from treadmill.utils import ObjectDict

from .base import Task
from .container import BuilderEnviron, SandboxEnviron, CompileTask, ExecuteTask
from .workspace import WorkspaceEnviron
from . import path
from . import ops


class JudgeTask(Task):
    def __init__(self, subm_sandbox, grader_sandbox):
        self.subm_sandbox: SandboxEnviron = subm_sandbox
        self.grader_sandbox: SandboxEnviron = grader_sandbox

    def _run(self):
        for testset in self.context.judge_spec.testsets:
            score = yield from self._judge_testset(testset)
            yield ops.UpdateJudgeResultOp(
                testset_id=testset.id,
                score=score
            )
        if self.context.total_score == self.context.judge_spec.total_score:
            yield ops.UpdateJudgeResultOp(status=JudgeStatus.PASSED)
        else:
            yield ops.UpdateJudgeResultOp(status=JudgeStatus.FAILED)

    def _judge_testset(self, testset):
        for testcase in testset.testcases:
            try:
                meta = yield from self._judge_testcase(testset, testcase)
                yield ops.UpdateJudgeResultOp(
                    testset_id=testset.id,
                    testcase_id=testcase.id,
                    testcase_status=TestCaseJudgeStatus.PASSED,
                    max_rss=meta.max_rss,
                    time=meta.time
                )
                continue
            except ServerFault as e:
                yield ops.UpdateJudgeResultOp(
                    testset_id=testset.id,
                    testcase_id=testcase.id,
                    testcase_status=TestCaseJudgeStatus.NOT_JUDGED,
                    error=e.message
                )
                raise
            except Timeout:
                yield ops.UpdateJudgeResultOp(
                    testset_id=testset.id,
                    testcase_id=testcase.id,
                    status=TestCaseJudgeStatus.TIME_LIMIT_EXCEEDED
                )
            except OutOfMemory:
                yield ops.UpdateJudgeResultOp(
                    testset_id=testset.id,
                    testcase_id=testcase.id,
                    status=TestCaseJudgeStatus.TIME_LIMIT_EXCEEDED
                )
            except SubmissionRuntimeError:
                yield ops.UpdateJudgeResultOp(
                    testset_id=testset.id,
                    testcase_id=testcase.id,
                    status=TestCaseJudgeStatus.RUNTIME_ERROR
                )
            except WrongAnswer:
                yield ops.UpdateJudgeResultOp(
                    testset_id=testset.id,
                    testcase_id=testcase.id,
                    status=TestCaseJudgeStatus.WRONG_ANSWER
                )
            return 0
        return testset.score

    def _judge_testcase(self, testset, testcase):
        result: ExecuteTask.Result = yield ExecuteTask(
            sandbox=self.subm_sandbox,
            stdin_file=path.test_input_file(testset, testcase),
            bin_file=path.subm_bin_file()
        )
        subm_exec_meta = result.meta

        if not result.ok:
            if result.is_fatal:
                raise IsolateExecutionError(result.output)
            elif result.timeout:
                raise Timeout()
            elif result.out_of_memory:
                raise OutOfMemory()
            else:
                raise SubmissionRuntimeError()

        if self.grader_sandbox:
            result: ExecuteTask.Result = ExecuteTask(
                sandbox=self.grader_sandbox,
                stdin_file=result.stdout_file,
                bin_file=path.grader_bin_file()
            ).run()

            if not result.ok:
                raise GraderRuntimeError(result.stderr)

        output_matches = yield ops.CompareFileOp(
            target=result.stdout_file,
            expected=path.test_output_file(testset, testcase)
        )

        if not output_matches:
            raise WrongAnswer()

        return subm_exec_meta


class CompileAllSourcesTask(Task):
    def _run(self):
        with BuilderEnviron(lang=self.context.subm_lang) as subm_builder:
            result = CompileTask(
                builder=subm_builder,
                src_file=self._subm_src_file,
                out_file=self._subm_bin_file
            ).run()

            if result.exit_code != 0:
                raise SubmissionCompileError(result.output)

            if self.context.grader:
                if self.context.grader_lang == self.context.subm_lang:
                    result = CompileTask(
                        builder=subm_builder,
                        src_file=self._grader_src_file,
                        out_file=self._grader_bin_file
                    ).run()
                else:
                    with BuilderEnviron(lang=self.context.grader_lang) as grader_builder:
                        result = CompileTask(
                            builder=grader_builder,
                            src_file=self._grader_src_file,
                            out_file=self._grader_bin_file
                        ).run()

                if result.exit_code != 0:
                    raise GraderCompileError(result.output)


class JudgeAllTestsTask(Task):
    class Result(ObjectDict):
        total_score: int

    def _run(self) -> Result:
        with ExitStack() as stack:
            subm_sandbox = SandboxEnviron(
                lang=self.context.subm_lang,
                isolated=True
            )
            stack.enter_context(subm_sandbox)
            if self.context.grader is not None:
                grader_sandbox = SandboxEnviron(
                    lang=self.context.grader_lang,
                    isolated=False
                )
                stack.enter_context(grader_sandbox)
            else:
                grader_sandbox = None

            result = self.Result(total_score=0)
            for testset in self.context.judge_spec.testsets:
                result = JudgeTestSetTask(
                    subm_sandbox=subm_sandbox,
                    grader_sandbox=grader_sandbox,
                    testset=testset
                ).run()
                result.total_score += result.score

            return result


class TreadmillJudgeTask(Task):
    def set_judge_result(self, *, status, score=None):
        self.context.api_client.set_judge_result(
            self.context.request.id,
            JudgeResult(status=status, score=score)
        )

    def run(self):
        try:
            self.context.submission = self.context.api_client.get_submission(self.context.request.submission_id)
            self.set_judge_result(status=JudgeStatus.IN_PROGRESS)
            with WorkspaceEnviron():
                CompileAllSourcesTask().run()
                result = JudgeAllTestsTask().run()
                if result.total_score >= self.context.judge_spec.total_score:
                    self.set_judge_result(status=JudgeStatus.PASSED, score=result.total_score)
                else:
                    self.set_judge_result(status=JudgeStatus.FAILED, score=result.total_score)
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

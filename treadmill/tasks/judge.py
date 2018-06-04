from treadmill.models import *
from treadmill.signal import *
from . import ops
from . import path
from .base import Task
from .container import SandboxEnviron, ExecuteTask


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
        result = yield ExecuteTask(
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

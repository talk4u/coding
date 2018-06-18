from treadmill.models import *
from treadmill.signal import *
from . import ops
from . import path
from .base import Task
from .container import SandboxEnviron, ExecuteResult, ExecuteSubmissionTask, ExecuteGraderTask


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
                    mem=meta.cg_mem,
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
                    testcase_status=TestCaseJudgeStatus.TIME_LIMIT_EXCEEDED
                )
            except OutOfMemory:
                yield ops.UpdateJudgeResultOp(
                    testset_id=testset.id,
                    testcase_id=testcase.id,
                    testcase_status=TestCaseJudgeStatus.MEMORY_LIMIT_EXCEEDED
                )
            except SubmissionRuntimeError as e:
                yield ops.UpdateJudgeResultOp(
                    testset_id=testset.id,
                    testcase_id=testcase.id,
                    testcase_status=TestCaseJudgeStatus.RUNTIME_ERROR,
                    error=e.message
                )
            except WrongAnswer:
                yield ops.UpdateJudgeResultOp(
                    testset_id=testset.id,
                    testcase_id=testcase.id,
                    testcase_status=TestCaseJudgeStatus.WRONG_ANSWER
                )
            return 0
        return testset.score

    def _judge_testcase(self, testset, testcase):
        result = yield ExecuteSubmissionTask(
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
                stderr = yield ops.ReadFileOp(result.stderr_file)
                stdout = yield ops.ReadFileOp(result.stdout_file)
                raise SubmissionRuntimeError(str({
                    'isolate_output': result.output,
                    'stderr': stderr,
                    'stdout': stdout
                }))

        if self.grader_sandbox:
            result = ExecuteGraderTask(
                sandbox=self.grader_sandbox,
                bin_file=path.grader_bin_file(),
                testcase_input_file=path.test_input_file(testset, testcase),
                testcase_output_file=result.stdout_file,
                solution_file=path.test_output_file(testset, testcase)
            ).run()

            if not result.ok:
                raise GraderRuntimeError(result.stderr)

            grader_output = yield ops.ReadFileOp(result.stdout_file)
            is_correct = grader_output == '1'  # '1': Correct, '0': Incorrect
        else:
            is_correct = yield ops.CompareFileOp(
                target=result.stdout_file,
                expected=path.test_output_file(testset, testcase)
            )

        if not is_correct:
            raise WrongAnswer()

        return subm_exec_meta

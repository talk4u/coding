from treadmill.models import TestCaseJudgeResult, TestSetJudgeResult, TestCaseJudgeStatus, JudgeResult
from treadmill.tasks.ops.base import Operation

__all__ = [
    'FetchSubmissionOp',
    'UpdateJudgeResultOp'
]


class FetchSubmissionOp(Operation):
    def __init__(self, submission_id):
        self.submission_id = submission_id

    def _run(self):
        subm = self.context.api_client.get_submission(self.submission_id)
        self.context.submission = subm
        self.context.judge_spec = judge_spec = subm.problem.judge_spec
        self.context.grader = judge_spec.grader
        if judge_spec.grader:
            self.context.grader_lang = judge_spec.grader.lang
        if self.context.sentry_client:
            self.context.sentry_client.user_context({
                'submission_id': subm.id,
                'problem_id': subm.problem.id
            })


def check_not_null(value):
    assert value is not None
    return value


class UpdateJudgeResultOp(Operation):
    def __init__(self, *,
                 testset_id=None,
                 testcase_id=None,
                 status=None,
                 testcase_status=None,
                 max_rss=None,
                 time=None,
                 score=None,
                 error=None):
        self.testset_id = testset_id
        self.testcase_id = testcase_id
        if testset_id is None:
            self.status = check_not_null(status)
            self.error = error
        elif testcase_id is None:
            self.score = check_not_null(score)
        else:
            self.testcase_status = testcase_status
            self.max_rss = max_rss
            self.time = time
            self.error = error

    def _run(self):
        if self.testset_id is None:
            self._update_judge_result()
        elif self.testcase_id is None:
            self._update_testset_result()
        else:
            self._update_testcase_result()

    def _update_testcase_result(self):
        if self.status == TestCaseJudgeStatus.PASSED:
            self.context.total_time += self.time
            self.context.max_rss = max(self.max_rss, self.context.max_rss)

        self.context.api_client.set_testcase_judge_result(
            self.context.request.id,
            self.testset_id,
            self.testcase_id,
            TestCaseJudgeResult(
                status=self.testcase_status,
                memory_used_bytes=self.max_rss,
                time_elapsed_seconds=self.time,
                error=self.error
            )
        )

    def _update_testset_result(self):
        self.context.total_score += self.score

        self.context.api_client.set_testset_judge_result(
            self.context.request.id,
            self.testset_id,
            TestSetJudgeResult(
                score=self.score
            )
        )

    def _update_judge_result(self):
        self.context.api_client.set_judge_result(
            self.context.request.id,
            JudgeResult(
                status=self.status,
                total_score=self.context.total_score,
                memory_used_bytes=self.context.max_rss,
                time_elapsed_seconds=self.context.total_time
            )
        )
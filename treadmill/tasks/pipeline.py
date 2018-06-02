from treadmill.models import JudgeStatus
from treadmill.signal import SubmissionCompileError, ServerFault, InternalApiError
from .workspace import WorkspaceEnviron
from .base import Task
from .stage import CompileStage, JudgeStage
from . import ops


class JudgePipeline(Task):
    def _run(self):
        try:
            yield ops.FetchSubmissionOp(self.context.request.submission_id)
            yield ops.UpdateJudgeResultOp(status=JudgeStatus.IN_PROGRESS)
            with WorkspaceEnviron():
                yield CompileStage()
                yield JudgeStage()
        except SubmissionCompileError as e:
            yield ops.UpdateJudgeResultOp(
                status=JudgeStatus.COMPILE_ERROR,
                error=e.message
            )
        except InternalApiError:
            self.context.log_current_error()
            raise
        except (ServerFault, Exception) as e:
            self.context.log_current_error()
            yield ops.ArchiveJudgeRequest()
            yield ops.UpdateJudgeResultOp(
                status=JudgeStatus.INTERNAL_ERROR,
                error=str(e)
            )
        except Exception as e:
            self.context.log_current_error()
            yield ops.ArchiveJudgeRequest()
            yield ops.UpdateJudgeResultOp(
                status=JudgeStatus.INTERNAL_ERROR,
                error=str(e)
            )


class RetryPipeline(Task):
    def _run(self):

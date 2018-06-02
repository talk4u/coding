from treadmill.models import JudgeRequest
from .base import Operation


__all__ = [
    'ArchiveJudgeRequest'
]


class ArchiveJudgeRequest(Operation):
    def _run(self):
        request_data = JudgeRequest.schema().dump(self.context.request)
        self.context.worker_factory.retry_worker().send(request_data)

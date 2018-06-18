import dramatiq
import traceback

from treadmill.tasks.base import Task

__all__ = [
    'RetryLaterOp',
    'EnqueueOp'
]


class RetryLaterOp(Task):
    def __init__(self, tb):
        self.traceback = traceback.format_tb(tb, limit=30)

    def _run(self):
        request_data = self.context.request.dump()
        message = dramatiq.Message(
            queue_name='treadmill_retry',
            actor_name='retry_worker',
            args=(request_data,),
            kwargs={
                'traceback': self.traceback
            },
            options={}
        )
        dramatiq.get_broker().enqueue(message)


class EnqueueOp(Task):
    def _run(self):
        request_data = self.context.request.dump()
        message = dramatiq.Message(
            queue_name='treadmill_normal',
            actor_name='judge_worker',
            args=(request_data,),
            kwargs={},
            options={}
        )
        dramatiq.get_broker().enqueue(message)

import dramatiq
from dramatiq.brokers.redis import RedisBroker

from treadmill.config import BaseConfig
from treadmill.context import JudgeContextFactory
from treadmill.models import JudgeRequest
from treadmill.signal import RetryableError
from treadmill.tasks import JudgePipeline
from treadmill.utils import cached

__all__ = [
    'WorkerFactory'
]


# Lower is faster
HIGH_PRIO = 0
NORMAL_PRIO = 50
LOW_PRIO = 100

NORMAL_QUEUE = 'treadmill.normal'
REJUDGE_QUEUE = 'treadmill.rejudge'
RETRY_QUEUE = 'treadmill.retry'


class WorkerFactory(object):
    def __init__(self, config: BaseConfig):
        self.config = config
        self.broker = RedisBroker(host=config.REDIS_HOST, port=config.REDIS_PORT)
        self.context_factory = JudgeContextFactory(config)

    def _judge(self, request_data):
        request = JudgeRequest.schema().load(request_data)
        with self.context_factory.new(request):
            try:
                JudgePipeline().run()
            except RetryableError:
                raise
            except Exception:
                self.retry_worker().send(request_data)

    def _retry(self, request):
        self.judge_worker().send(request)

    @cached
    def judge_worker(self):
        return dramatiq.Actor(
            self._judge,
            broker=self.broker,
            actor_name='judge_worker',
            queue_name='normal',
            priority=NORMAL_PRIO,
            options={}
        )

    @cached
    def retry_worker(self):
        return dramatiq.Actor(
            self._retry,
            broker=self.broker,
            actor_name='retry_worker',
            queue_name='failed',
            priority=LOW_PRIO,
            options={}
        )

    @cached
    def rejudge_worker(self):
        return dramatiq.Actor(
            self._judge,
            broker=self.broker,
            actor_name='rejudge_worker',
            queue_name='rejudge',
            priority=LOW_PRIO,
            options={}
        )

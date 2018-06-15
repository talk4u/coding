import logging

import dramatiq
from dramatiq.brokers.redis import RedisBroker

from treadmill.config import BaseConfig, DevConfig
from treadmill.context import JudgeContextFactory
from treadmill.models import JudgeRequest
from treadmill.signal import RetryableError
from treadmill.tasks import JudgePipeline, EnqueuePipeline
from treadmill.utils import cached

__all__ = [
    'WorkerFactory'
]


_logger = logging.getLogger('treadmill.worker')


# Lower is faster
HIGH_PRIO = 0
NORMAL_PRIO = 50
LOW_PRIO = 100

NORMAL_QUEUE = 'treadmill_normal'
REJUDGE_QUEUE = 'treadmill_rejudge'
RETRY_QUEUE = 'treadmill_retry'


class WorkerFactory(object):
    def __init__(self, config: BaseConfig):
        self.config = config
        self.broker = RedisBroker(host=config.REDIS_HOST, port=config.REDIS_PORT)
        dramatiq.set_broker(self.broker)
        self.context_factory = JudgeContextFactory(config)

    def _judge(self, request_data):
        request = JudgeRequest(**request_data)
        _logger.info('Received ' + str(request))
        with self.context_factory.new(request):
            try:
                JudgePipeline().run()
            except RetryableError:
                raise
            except Exception as e:
                _logger.exception(e)
                self.retry_worker().send(request_data)

    def _retry(self, request_data):
        request = JudgeRequest(**request_data)
        _logger.info('Received ' + str(request))
        with self.context_factory.new(request):
            try:
                EnqueuePipeline().run()
                self.judge_worker().send(request_data)
            except Exception as e:
                _logger.exception(e)
                raise

    @cached
    def judge_worker(self):
        return dramatiq.Actor(
            self._judge,
            broker=self.broker,
            actor_name='judge_worker',
            queue_name=NORMAL_QUEUE,
            priority=NORMAL_PRIO,
            options={}
        )

    @cached
    def retry_worker(self):
        return dramatiq.Actor(
            self._retry,
            broker=self.broker,
            actor_name='retry_worker',
            queue_name=RETRY_QUEUE,
            priority=LOW_PRIO,
            options={}
        )

    @cached
    def rejudge_worker(self):
        return dramatiq.Actor(
            self._judge,
            broker=self.broker,
            actor_name='rejudge_worker',
            queue_name=REJUDGE_QUEUE,
            priority=LOW_PRIO,
            options={}
        )


def main():
    treadmill_logger = logging.getLogger('treadmill')
    treadmill_logger.setLevel(logging.DEBUG)
    treadmill_logger.addHandler(logging.StreamHandler())
    factory = WorkerFactory(DevConfig(
        HOST_WORKSPACE_ROOT='/Users/jjong/Temp/treadmill-workspace',
        S3FS_ROOT='/Users/jjong/mnt/talk4u-data'
    ))
    request = JudgeRequest(
        id=1,
        problem_id=1,
        submission_id=3
    ).dump()
    factory.judge_worker().send(request)


if __name__ == '__main__':
    main()

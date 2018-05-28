import argparse
import importlib

import dramatiq
from dramatiq.brokers.redis import RedisBroker

from treadmill.models import JudgeRequest
from treadmill.context import JudgeContextFactory
from treadmill.config import TreadmillConfig
from treadmill.tasks import TreadmillJudgeTask


# Lower is faster
NORMAL_PRIO = 0
REJUDGE_PRIO = 10


class WorkerFactory(object):
    def __init__(self, config: TreadmillConfig):
        self.config = config
        self.broker = RedisBroker(host=config.REDIS_HOST, port=config.REDIS_PORT)
        self.context_factory = JudgeContextFactory(config)

    def judge_task(self, request: JudgeRequest):
        with self.context_factory.new(request) as context:
            TreadmillJudgeTask().run(context)

    def judge_worker(self):
        return dramatiq.Actor(
            self.judge_task,
            broker=self.broker,
            actor_name='judge_worker',
            queue_name='normal',
            priority=NORMAL_PRIO,
            options={}
        )

    def rejudge_worker(self):
        return dramatiq.Actor(
            self.judge_task,
            broker=self.broker,
            actor_name='rejudge_worker',
            queue_name='rejudge',
            priority=REJUDGE_PRIO,
            options={}
        )


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'config', type=str, dest='config_class',
        help='Configuration class to use (LocalConfig, StagingConfig, ProdConfig)'
    )
    parser.add_argument(
        '--rejudge-only', '-R', type=bool, dest='rejudge_only',
        help='Run rejudge actors only'
    )

    args = parser.parse_args()

    config_module = importlib.import_module('treadmill.config')
    args.config = getattr(config_module, args.config_class)()
    if args.config is None:
        raise ValueError(f'No config class named {args.config_class}')

    return args


def main():
    args = parse_arguments()
    factory = WorkerFactory(args.config)

    # Declare required
    if args.rejudge_only:
        factory.rejudge_worker()
    else:
        factory.judge_worker()
        factory.rejudge_worker()


if __name__ == '__main__':
    main()

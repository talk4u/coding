import os
import importlib

from treadmill.worker import WorkerFactory

config_name = os.environ.get('TM_CONFIG')
if config_name is None:
    raise ValueError('Set TREADMILL_CONFIG environment variable')

config = getattr(importlib.import_module('treadmill.config'), config_name)
if config is None:
    raise ValueError(f'{config_name} does not exist in treadmill.config module')

worker_factory = WorkerFactory(config)
worker_factory.judge_worker()
worker_factory.rejudge_worker()
worker_factory.retry_worker()

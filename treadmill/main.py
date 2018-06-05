import os
import importlib

from treadmill.worker import WorkerFactory

config_name = os.environ.get('TM_CONFIG')
if config_name is None:
    raise ValueError('Set TREADMILL_CONFIG environment variable')

config_type = getattr(importlib.import_module('treadmill.config'), config_name)
if config_type is None:
    raise ValueError(f'{config_name} does not exist in treadmill.config module')

worker_factory = WorkerFactory(config_type())
worker_factory.judge_worker()
worker_factory.rejudge_worker()
worker_factory.retry_worker()

from datetime import datetime

import dramatiq
from django.conf import settings
from dramatiq.brokers.redis import RedisBroker


broker = RedisBroker(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
dramatiq.set_broker(broker)


@dramatiq.actor(queue_name='treadmill_normal')
def judge_worker(request):
    """ Dummy worker """
    pass


@dramatiq.actor(queue_name='treadmill_rejudge')
def rejudge_worker(request):
    """ Dummy worker """
    pass


def judge(request_id, problem_id, submission_id):
    judge_worker.send({
        'id': request_id,
        'problem_id': problem_id,
        'submission_id': submission_id,
        'created_at': datetime.now().isoformat()
    })


def rejudge(request_id, problem_id, submission_id):
    rejudge_worker.send({
        'id': request_id,
        'problem_id': problem_id,
        'submission_id': submission_id,
        'created_at': datetime.now().isoformat()
    })

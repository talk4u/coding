import traceback
import threading

import docker
import raven

from treadmill.models import JudgeRequest, Submission, JudgeSpec, Grader, Lang
from treadmill.clients import APIClient
from treadmill.config import TreadmillConfig
from treadmill.worker import WorkerFactory


global_context = threading.local()


def get_current_context() -> 'JudgeContext':
    global global_context
    return global_context.current


def set_current_context(context):
    global global_context
    global_context.current = context


class ContextMixin(object):
    @property
    def context(self) -> 'JudgeContext':
        return get_current_context()


class JudgeContextFactory(object):
    def __init__(self, config):
        self.config = config
        self.docker_client = docker.from_env()
        self.api_client = APIClient(config)
        self.sentry_client = config.SENTRY_DSN and raven.Client(config.SENTRY_DSN)
        self.worker_factory = WorkerFactory(config)

    def new(self, request):
        return JudgeContext(
            request=request,
            config=self.config,
            docker_client=self.docker_client,
            api_client=self.api_client,
            sentry_client=self.sentry_client,
            worker_factory=self.worker_factory
        )


class JudgeContext(object):
    request: JudgeRequest
    config: TreadmillConfig
    submission: Submission
    judge_spec: JudgeSpec
    subm_lang: Lang
    grader: Grader
    grader_lang: Lang

    total_score: int = 0
    total_time: float = 0.0
    max_rss: int = 0

    docker_client: docker.DockerClient
    api_client: APIClient
    sentry_client: raven.Client
    worker_factory: WorkerFactory

    def __init__(self, *,
                 request: JudgeRequest,
                 config: TreadmillConfig,
                 docker_client: docker.DockerClient,
                 api_client: APIClient,
                 sentry_client: raven.Client,
                 worker_factory: WorkerFactory):
        self.request = request
        self.config = config

        self.total_score = 0
        self.total_time = 0
        self.max_rss = 0

        self.docker_client = docker_client
        self.api_client = api_client
        self.sentry_client = sentry_client
        self.worker_factory = worker_factory

    def __enter__(self):
        set_current_context(self)
        if self.sentry_client:
            self.sentry_client.context.activate()
            self.sentry_client.user_context({
                'request_id': self.request.id
            })

    def __exit__(self, exc_type, exc_val, exc_tb):
        set_current_context(None)
        if self.sentry_client:
            self.sentry_client.context.clear()

    def __getattr__(self, item):
        return None

    def log_current_error(self):
        if self.sentry_client:
            self.sentry_client.captureException()
        else:
            traceback.print_exc()

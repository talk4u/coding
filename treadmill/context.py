import os

import docker
import raven

from treadmill.models import JudgeRequest, Submission, JudgeSpec, Grader, Lang
from treadmill.clients import APIClient
from treadmill.config import TreadmillConfig


class JudgeContextFactory(object):
    def __init__(self, config):
        self.config = config
        self.docker_client = docker.from_env()
        self.api_client = APIClient(config)
        self.sentry_client = config.SENTRY_DSN and raven.Client(config.SENTRY_DSN)

    def new(self, request):
        return JudgeContext(
            request=request,
            config=self.config,
            docker_client=self.docker_client,
            api_client=self.api_client,
            sentry_client=self.sentry_client
        )


class JudgeContext(object):
    def __init__(self, *,
                 request: JudgeRequest,
                 config: TreadmillConfig,
                 docker_client: docker.DockerClient,
                 api_client: APIClient,
                 sentry_client: raven.Client):
        self.request = request
        self.config = config
        self._subm: Submission = None
        self.judge_spec: JudgeSpec = None
        self.subm_lang: Lang = None
        self.grader: Grader = None
        self.grader_lang: Lang = None

        self.host_workspace_dir = os.path.join(config.HOST_WORKSPACE_ROOT, str(request.id))
        self.s3fs_dir = config.S3FS_ROOT
        self.container_workspace_dir = '/workspace'
        self.sandbox_dir = '/sandbox'

        self.docker_client = docker_client
        self.api_client = api_client
        self.sentry_client = sentry_client

    def __enter__(self):
        if self.sentry_client:
            self.sentry_client.context.activate()
            self.sentry_client.user_context({
                'request_id': self.request.id
            })

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.sentry_client:
            self.sentry_client.context.clear()

    @property
    def submission(self):
        return self._subm

    @submission.setter
    def submission(self, submission):
        self._subm = submission
        self.judge_spec = submission.problem.judge_spec
        self.subm_lang = submission.lang
        self.grader = self.judge_spec.grader
        if self.grader:
            self.grader_lang = self.grader.lang
        if self.sentry_client:
            self.sentry_client.user_context({
                'submission_id': self._subm.id,
                'problem_id': self._subm.problem.id
            })

    def host_path(self, path):
        return os.path.join(self.host_workspace_dir, *path)

    def s3fs_path(self, path):
        return os.path.join(self.s3fs_dir, *path)

    def container_path(self, path):
        return os.path.join(self.container_workspace_dir, path)

    def sandbox_path(self, path):
        if path[0].startswith == 'sandbox':
            path[0] = path[0][7:]
        return os.path.join(self.sandbox_dir, *path)

    def log_current_error(self):
        if self.sentry_client:
            self.sentry_client.captureException()

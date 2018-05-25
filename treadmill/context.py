import os

import docker

from treadmill.models import JudgeRequest, Submission, JudgeSpec
from treadmill.client import APIClient
from treadmill.config import TreadmillConfig


class JudgeContext(object):
    def __init__(self, request: JudgeRequest, config: TreadmillConfig):
        self._request = request
        self._config = config

        # Submission variables

        self._submission: Submission = None
        self._judge_spec: JudgeSpec = None
        self._subm_lang = None
        self._grader = None
        self._grader_lang = None

        # Path variables

        self._host_workspace_dir = os.path.join(config.HOST_WORKSPACE_ROOT, str(request.id))
        self._s3fs_dir = config.S3FS_ROOT
        self._container_workspace_dir = '/workspace'
        self._sandbox_dir = '/sandbox'

        # Clients

        self.docker_client: docker.DockerClient = docker.from_env()
        self.api_client = APIClient(config)

    @property
    def request(self):
        return self._request

    @property
    def config(self):
        return self._config

    @property
    def submission(self):
        return self._submission

    @submission.setter
    def submission(self, subm: Submission):
        assert isinstance(subm, Submission)
        self._submission = subm
        self._subm_lang = subm.lang
        self._judge_spec = subm.problem.judge_spec
        self._grader = self._judge_spec.grader
        if self._grader:
            self._grader_lang = self._grader.lang

    @property
    def judge_spec(self):
        return self._judge_spec

    @property
    def subm_lang(self):
        return self._subm_lang

    @property
    def grader(self):
        return self._grader

    @property
    def grader_lang(self):
        return self._grader_lang

    @property
    def host_workspace_dir(self):
        return self._host_workspace_dir

    @property
    def host_s3fs_dir(self):
        return self._s3fs_dir

    @property
    def container_workspace_dir(self):
        return self._container_workspace_dir

    @property
    def sandbox_dir(self):
        return self._sandbox_dir

    def host_path(self, path):
        return os.path.join(self._host_workspace_dir, *path)

    def s3fs_path(self, path):
        return os.path.join(self._s3fs_dir, *path)

    def container_path(self, path):
        return os.path.join(self._container_workspace_dir, path)

    def sandbox_path(self, path):
        if path[0].startswith == 'sandbox':
            path[0] = path[0][7:]
        return os.path.join(self._sandbox_dir, *path)

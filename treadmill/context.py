import os

import treadmill.models as models
from treadmill.config import TreadmillConfig
from treadmill.data import LANG_PROFILES


class JudgeContext(object):
    def __init__(self, *,
                 request: models.JudgeRequest,
                 submission: models.Submission,
                 config: TreadmillConfig):
        self.request = request
        self.submission = submission
        self.judge_spec = submission.problem.judge_spec
        self.config = config

    def get_s3_path(self, *args):
        return os.path.join(self.config.S3FS_ROOT,
                            self.judge_spec.root_dir,
                            *args)

    def get_host_workspace_path(self, *args):
        return os.path.join(self.config.HOST_WORKSPACE_ROOT,
                            str(self.request.id),
                            self.host_workspace_dir, *args)

    @property
    def host_workspace_dir(self):
        return self.get_host_workspace_path('')

    @property
    def src_lang(self):
        return self.submission.lang_profile

    @property
    def src_lang_profile(self):
        return LANG_PROFILES.get(self.src_lang)

    @property
    def has_grader(self):
        return self.judge_spec.grader is not None

    @property
    def grader_lang(self):
        return self.judge_spec.grader.lang_profile

    @property
    def grader_lang_profile(self):
        return LANG_PROFILES.get(self.grader_lang)

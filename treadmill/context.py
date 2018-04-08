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

    def host_s3_path(self, *args):
        return os.path.join(self.config.S3FS_ROOT,
                            self.judge_spec.root_dir,
                            *args)

    def host_path(self, *args):
        return os.path.join(self.config.HOST_WORKSPACE_ROOT,
                            str(self.request.id),
                            *args)

    @property
    def host_workspace_dir(self):
        return self.host_path('')

    @property
    def submission_lang(self):
        return self.submission.lang_profile

    @property
    def submission_lang_profile(self):
        return LANG_PROFILES.get(self.submission_lang)

    @property
    def grader(self):
        return self.judge_spec.grader

    @property
    def grader_lang(self):
        return self.judge_spec.grader.lang_profile

    @property
    def grader_lang_profile(self):
        return LANG_PROFILES.get(self.grader_lang)

import requests
from treadmill.config import TreadmillConfig
from treadmill.models import Submission


class APIClient(object):
    def __init__(self, config: TreadmillConfig):
        self._config = config

    def get_submission_detail(self) -> Submission:
        pass

    def set_compile_error(self, request_id, error_msg):
        pass

    def set_internal_error(self, request_id, **data):
        pass

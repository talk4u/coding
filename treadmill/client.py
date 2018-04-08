import requests
from treadmill.config import *


class APIClient(object):
    def __init__(self, config: TreadmillConfig):
        self._config = config

    def set_compile_error(self, request_id, error_msg):
        pass

    def set_internal_error(self, request_id, **data):
        pass

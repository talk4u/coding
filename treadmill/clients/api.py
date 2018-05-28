import requests

from treadmill.config import TreadmillConfig
from treadmill.models import Submission, TestCaseJudgeResult, TestSetJudgeResult, JudgeResult
from treadmill.signal import InternalApiError
from treadmill.utils import DataClass


class APIClient(object):
    def __init__(self, config: TreadmillConfig):
        self._config = config
        self._sess = requests.Session()
        self._sess.headers['Authorization'] = self._config.API_TOKEN

    def _get(self, path, **kwargs):
        return self._sess.get(self._config.API_ENDPOINT + path, **kwargs)

    def _post(self, path, data, **kwargs):
        if isinstance(data, DataClass):
            data = data.schema().dump(data)
        return self._sess.post(self._config.API_ENDPOINT + path, data=data, **kwargs)

    def get_submission(self, subm_id) -> Submission:
        resp = self._get(f'/submissions/{subm_id}')
        if resp.ok:
            return Submission.schema().load(resp.json())
        else:
            raise InternalApiError(resp.text)

    def save_testcase_judge_result(self, req_id, testset_id, testcase_id, result: TestCaseJudgeResult):
        resp = self._post(f'/judge/{req_id}/{testset_id}/{testcase_id}/', result)
        if not resp.ok:
            raise InternalApiError(resp.text)

    def save_testset_judge_result(self, req_id, testset_id, result: TestSetJudgeResult):
        resp = self._post(f'/judge/{req_id}/{testset_id}/', result)
        if not resp.ok:
            raise InternalApiError(resp.text)

    def save_judge_result(self, req_id, result: JudgeResult):
        resp = self._post(f'/judge/{req_id}/', result)
        if not resp.ok:
            raise InternalApiError(resp.text)

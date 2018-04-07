import enum
from datetime import datetime
from typing import Optional, List

from treadmill.config import TreadmillConfig
from treadmill.schema_util import DataClass


S3Key = str


class TestCase(DataClass):
    id: int
    input_file: S3Key
    output_file: S3Key
    created_at: datetime


class TestSet(DataClass):
    id: int
    cases: List[TestCase]
    created_at: datetime
    updated_at: datetime


class Grader(DataClass):
    grader_file: S3Key
    created_at: datetime
    updated_at: datetime


class JudgeSpec(DataClass):
    root_dir: S3Key
    sets: List[TestSet]
    grader: Optional[Grader]
    mem_limit_bytes: int
    time_limit_seconds: float
    file_size_limit_kilos: Optional[int] = 0
    updated_at: datetime


class Problem(DataClass):
    judge_spec: JudgeSpec


class LanguageProfile(enum.Enum):
    cpp = 'c++'
    java = 'java'
    python3 = 'python3'
    go = 'go'

    @classmethod
    def choices(cls):
        return [(p.value, p.name) for p in cls]


class Submission(DataClass):
    user_id: int
    problem: Problem
    lang_profile: LanguageProfile


class JudgeStatus(enum.Enum):
    enqueued = 'ENQ'
    in_progress = 'IP'
    compile_error = 'CTE'
    passed = 'PASS'
    failed = 'FAIL'

    @classmethod
    def choices(cls):
        return [(p.value, p.name) for p in cls]


class TestCaseJudgeStatus(enum.Enum):
    not_judged = 'NA'
    runtime_error = 'RTE'
    wrong_answer = 'WA'
    memory_limit_exceeded = 'MLE'
    time_limit_exceeded = 'TLE'
    correct = 'PASS'

    @classmethod
    def choices(cls):
        return [(p.value, p.name) for p in cls]


class TestCaseJudgeResult(DataClass):
    id: int
    status: TestCaseJudgeStatus
    memory_used_bytes: Optional[int]
    time_elapsed_seconds: Optional[float]
    error_msg: Optional[str]
    judged_at: datetime


class TestSetJudgeResult(DataClass):
    id: int
    case_results: List[TestCaseJudgeResult]


class JudgeResult(DataClass):
    request_id: int
    submission_id: int
    set_results: List[TestSetJudgeResult]
    judged_at: datetime


class JudgeRequest(DataClass):
    id: int
    submission: Submission
    is_rejudge: bool
    created_at: datetime


class JudgeContext(object):
    config: TreadmillConfig
    submission: Submission
    judge_spec: JudgeSpec
    workspace_dir: str

    def __init__(self, submission, config):
        self.submission = submission
        self.judge_spec = submission.problem.judge_spec
        self.config = config

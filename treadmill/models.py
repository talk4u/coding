import enum
from datetime import datetime
from typing import Optional, List

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


class LanguageProfile(enum.Enum):
    cpp = 'c++'
    java = 'java'
    python3 = 'python3'
    go = 'go'

    @classmethod
    def choices(cls):
        return [(p.value, p.name) for p in cls]


class Grader(DataClass):
    grader_file: S3Key
    lang_profile: LanguageProfile
    created_at: datetime
    updated_at: datetime


class JudgeSpec(DataClass):
    root_dir: S3Key
    sets: List[TestSet]
    grader: Optional[Grader]
    mem_limit_bytes: int
    time_limit_seconds: float
    file_size_limit_kilos: int = 0
    pid_limits: int = 1
    updated_at: datetime


class Problem(DataClass):
    judge_spec: JudgeSpec


class Submission(DataClass):
    id: int
    user_id: int
    problem: Problem
    src_file: S3Key
    lang_profile: LanguageProfile


class JudgeStatus(enum.Enum):
    enqueued = 'ENQ'
    in_progress = 'IP'
    compile_error = 'CTE'
    passed = 'PASS'
    failed = 'FAIL'
    internal_error = 'ERR'

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
    request_id: str  # UUID
    submission_id: int
    set_results: List[TestSetJudgeResult]
    judged_at: datetime


class JudgeRequest(DataClass):
    id: str  # UUID
    submission_id: int
    is_rejudge: bool
    created_at: datetime

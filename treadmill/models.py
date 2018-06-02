import enum
from datetime import datetime
from typing import Optional, List

from treadmill.utils import DataModel


S3Key = str


class TestCase(DataModel):
    id: int  # index from 0
    input_file: S3Key
    output_file: S3Key
    created_at: datetime


class TestSet(DataModel):
    id: int  # index from 0
    score: int
    testcases: List[TestCase]
    created_at: datetime
    updated_at: datetime


class LangProfile(enum.Enum):
    CPP = ('g++ 6.4.0', 'main.cpp', 'main')
    JAVA = ('OpenJDK 8u151', 'Main.java', 'Main.class')
    PYTHON3 = ('Python 3.6.5', 'main.py', 'main.py')
    GO = ('Go 1.10.1', 'main.go', 'main')

    def __init__(self, version, src_file_name, bin_file_name):
        self.version = version
        self.src_file_name = src_file_name
        self.bin_file_name = bin_file_name


class Lang(enum.Enum):
    CPP = 'c++'
    JAVA = 'java'
    PYTHON3 = 'python3'
    GO = 'go'

    @property
    def profile(self) -> LangProfile:
        return getattr(LangProfile, self.name)

    @classmethod
    def choices(cls):
        return [(p.value, p.name) for p in cls]


class Grader(DataModel):
    src_file: S3Key
    lang: Lang
    created_at: datetime
    updated_at: datetime


class JudgeSpec(DataModel):
    total_score: int
    testsets: List[TestSet]
    grader: Optional[Grader]
    mem_limit_bytes: int
    time_limit_seconds: float
    file_size_limit_kilos: int = 0
    pid_limits: int = 1
    updated_at: datetime


class Problem(DataModel):
    judge_spec: JudgeSpec


class Submission(DataModel):
    id: int
    user_id: int
    problem: Problem
    src_file: S3Key
    lang: Lang


class JudgeStatus(enum.Enum):
    ENQUEUED = 'ENQ'
    IN_PROGRESS = 'IP'
    COMPILE_ERROR = 'CTE'
    PASSED = 'PASS'
    FAILED = 'FAIL'
    INTERNAL_ERROR = 'ERR'

    @classmethod
    def choices(cls):
        return [(p.value, p.name) for p in cls]


class TestCaseJudgeStatus(enum.Enum):
    NOT_JUDGED = 'NA'
    RUNTIME_ERROR = 'RTE'
    WRONG_ANSWER = 'WA'
    MEMORY_LIMIT_EXCEEDED = 'MLE'
    TIME_LIMIT_EXCEEDED = 'TLE'
    PASSED = 'PASS'

    @classmethod
    def choices(cls):
        return [(p.value, p.name) for p in cls]


class TestCaseJudgeResult(DataModel):
    status: TestCaseJudgeStatus
    memory_used_bytes: Optional[int] = 0
    time_elapsed_seconds: Optional[float] = 0.0
    error_msg: Optional[str] = None


class TestSetJudgeResult(DataModel):
    score: int


class JudgeResult(DataModel):
    status: JudgeStatus
    error: Optional[str]
    total_score: int
    time_elapsed_seconds: float
    memory_used_bytes: int


class JudgeRequest(DataModel):
    id: int
    submission_id: int
    rejudge: bool
    created_at: datetime


class IsolateExecMeta(object):
    """
    From http://www.ucw.cz/moe/isolate.1.html

        The meta-file contains miscellaneous meta-information on execution of the
        program within the sandbox. It is a textual file consisting of lines of
        format key:value.

    In normal execution the meta output looks like:

        time:0.000
        time-wall:0.085
        max-rss:548
        csw-voluntary:5
        csw-forced:1
        exitcode:0
    """

    @classmethod
    def parse(cls, data):
        props = {
            k: ':'.join(v)
            for line in data.split('\n')
            for k, *v in line.split(':')
        }
        return IsolateExecMeta(**props)

    def __init__(self, **props):
        self._props = props

    @property
    def killed(self):
        """
        Present when the program was terminated by the sandbox
        (e.g., because it has exceeded the time limit).
        """
        killed = self._props.get('killed')
        return killed is not None

    @property
    def time(self):
        """Run time of the program in fractional seconds."""
        time = self._props.get('time')
        if time is not None:
            return float(time)

    @property
    def time_wall(self):
        """Wall clock time of the program in fractional seconds."""
        time_wall = self._props.get('time-wall')
        if time_wall is not None:
            return float(time_wall)

    @property
    def max_rss(self):
        """Maximum resident set size of the process (in bytes)."""
        max_rss = self._props.get('max-rss')
        if max_rss is not None:
            return int(max_rss) * 1024

    @property
    def message(self):
        """
        Status message, not intended for machine processing.
        E.g., "Time limit exceeded."
        """
        return self._props.get('message')

    @property
    def csw_forced(self):
        """Number of context switches forced by the kernel."""
        csw_forced = self._props.get('csw-forced')
        if csw_forced is not None:
            return int(csw_forced)

    @property
    def csw_voluntary(self):
        """
        Number of context switches caused by the process giving up the CPU
        voluntarily.
        """
        csw_voluntary = self._props.get('csw-voluntary')
        if csw_voluntary is not None:
            return int(csw_voluntary)

    @property
    def exitcode(self):
        """The program has exited normally with this exit code."""
        exitcode = self._props.get('exitcode')
        if exitcode is not None:
            return int(exitcode)

    @property
    def exitsig(self):
        """The program has exited after receiving this fatal signal."""
        exitsig = self._props.get('exitsig')
        if exitsig is not None:
            return int(exitsig)

    @property
    def cg_mem(self):
        """
        When control groups are enabled, this is the total memory use by the
        whole control group (in bytes).
        """
        cg_mem = self._props.get('cg_mem')
        if cg_mem is not None:
            return int(cg_mem) * 1000

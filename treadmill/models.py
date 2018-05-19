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


class Lang(enum.Enum):
    CPP = 'c++'
    JAVA = 'java'
    PYTHON3 = 'python3'
    GO = 'go'

    def __init__(self, value):
        if value == 'c++':
            self.src_file_name = 'main.cpp'
            self.bin_file_name = 'main'
        elif value == 'java':
            self.src_file_name = 'Main.java'
            self.bin_file_name = 'Main.class'
        elif value == 'python3':
            self.src_file_name = 'main.py'
            self.bin_file_name = 'main.py'
        elif value == 'go':
            self.src_file_name = 'main.go'
            self.bin_file_name = 'main'

    @classmethod
    def choices(cls):
        return [(p.value, p.name) for p in cls]


class Grader(DataClass):
    grader_file: S3Key
    lang_profile: Lang
    created_at: datetime
    updated_at: datetime


class JudgeSpec(DataClass):
    root_dir: S3Key
    testsets: List[TestSet]
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
    lang_profile: Lang


class JudgeStatus(enum.Enum):
    ENQUEUED = 'ENQ'
    IN_PROGRESS = 'IP'
    COMPILE_ERROR = 'CTE'
    PASS = 'PASS'
    FAIL = 'FAIL'
    INTERNAL_ERROR = 'ERR'

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

    def killed(self):
        """
        Present when the program was terminated by the sandbox
        (e.g., because it has exceeded the time limit).
        """
        killed = self._props.get('killed')
        return killed is not None

    def time(self):
        """Run time of the program in fractional seconds."""
        time = self._props.get('time')
        if time is not None:
            return float(time)

    def time_wall(self):
        """Wall clock time of the program in fractional seconds."""
        time_wall = self._props.get('time-wall')
        if time_wall is not None:
            return float(time_wall)

    def max_rss(self):
        """Maximum resident set size of the process (in bytes)."""
        max_rss = self._props.get('max-rss')
        if max_rss is not None:
            return int(max_rss) * 1000

    def message(self):
        """
        Status message, not intended for machine processing.
        E.g., "Time limit exceeded."
        """
        return self._props.get('message')

    def csw_forced(self):
        """Number of context switches forced by the kernel."""
        csw_forced = self._props.get('csw-forced')
        if csw_forced is not None:
            return int(csw_forced)

    def csw_voluntary(self):
        """
        Number of context switches caused by the process giving up the CPU
        voluntarily.
        """
        csw_voluntary = self._props.get('csw-voluntary')
        if csw_voluntary is not None:
            return int(csw_voluntary)

    def exitcode(self):
        """The program has exited normally with this exit code."""
        exitcode = self._props.get('exitcode')
        if exitcode is not None:
            return int(exitcode)

    def exitsig(self):
        """The program has exited after receiving this fatal signal."""
        exitsig = self._props.get('exitsig')
        if exitsig is not None:
            return int(exitsig)

    def cg_mem(self):
        """
        When control groups are enabled, this is the total memory use by the
        whole control group (in bytes).
        """
        cg_mem = self._props.get('cg_mem')
        if cg_mem is not None:
            return int(cg_mem) * 1000
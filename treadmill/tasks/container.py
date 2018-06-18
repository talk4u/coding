import os
import uuid
from typing import Optional

from docker.models.containers import Container

from treadmill.context import ContextMixin
from treadmill.models import Lang, IsolateExecMeta
from treadmill.signal import UnsupportedLanguage, IsolateInitFail
from treadmill.utils import ObjectDict
from .base import Environ, Task
from . import ops
from . import path

__all__ = [
    'BuilderEnviron',
    'SandboxEnviron',
    'CompileTask',
    'ExecuteResult',
    'ExecuteSubmissionTask',
    'ExecuteGraderTask'
]


class BuilderEnviron(Environ):
    def __init__(self, *, lang):
        self.lang = lang
        self.container: Container = None

    def _setup(self):
        container_tag = self.lang.profile.builder_image_tag(self.context.config)
        if container_tag is None:
            raise UnsupportedLanguage(self.lang)
        self.container = yield ops.RunDockerContainerOp(
            container_tag=container_tag,
        )

    def _teardown(self):
        if self.container:
            yield ops.KillDockerContainerOp(self.container)

    def compile(self, src_file, out_file):
        src_file = src_file.container_path
        out_file = out_file.container_path

        result = yield ops.ExecInDockerContainerOp(
            container=self.container,
            cmd=self.lang.profile.get_compile_cmd(src_file, out_file)
        )
        return result


class SandboxEnviron(Environ):
    # `dir_in` in container is seen as `dir_out` in isolated sandbox
    _sandbox_mapping_opt = '--dir={dir_in}={dir_out}:rw'.format(
        dir_in=path.SANDBOX_ROOT.sandbox_path,
        dir_out=path.SANDBOX_ROOT.container_path
    )
    _etc_mapping_opt = '--dir={dir_in}={dir_out}:rw'.format(
        dir_in=path.ETC.sandbox_path,
        dir_out=path.ETC.container_path
    )

    def __init__(self, *, lang, isolated):
        self.lang = lang
        self.container = None
        self.isolated = isolated

    def _setup(self):
        container_tag = self.lang.profile.sandbox_image_tag(self.context.config)
        if container_tag is None:
            raise UnsupportedLanguage(self.lang)

        self.container = yield ops.RunDockerContainerOp(
            container_tag=self.context.config.sandbox_container_tag(self.lang),
            privileged=self.isolated
        )

        if self.isolated:
            init_result = yield ops.ExecInDockerContainerOp(
                container=self.container,
                cmd=['isolate', '--cg', '--init']
            )
            if init_result.exit_code != 0:
                raise IsolateInitFail(init_result.output)

    def _teardown(self):
        if self.container:
            yield ops.KillDockerContainerOp(self.container)

    def _exec_normal(self, *, bin_file, stdout_file, args=()):
        result = yield ops.ExecInDockerContainerOp(
            self.container,
            cmd=[
                *self.lang.profile.get_exec_cmd(bin_file, args),
                '1>', stdout_file
            ],
            privileged=False
        )
        return result

    def _exec_in_isolate(self, *, bin_file, stdin_file, stdout_file, stderr_file,
                         meta_file, limits, args=()):
        pid_limits = limits.pid_limits
        if self.lang == Lang.JAVA:
            # For not-yet-known reason JVM requires at least 11 processes to run
            pid_limits = 16

        mapping_opts = [self._sandbox_mapping_opt]
        if self.lang == Lang.PYTHON3:
            mapping_opts += [self._etc_mapping_opt]  # Python requires /etc/passwd file

        result = yield ops.ExecInDockerContainerOp(
            container=self.container,
            cmd=[
                'isolate',
                *mapping_opts,
                '--cg',
                f'--meta={meta_file}',
                f'--cg-mem={limits.mem_limit_bytes // 1024 * 2}',
                f'--time={limits.time_limit_seconds}',
                f'--wall-time={limits.time_limit_seconds * 3}',
                f'--extra-time=1.0',
                f'--fsize={limits.file_size_limit_kilos}',
                f'--processes={pid_limits}',
                f'--stdin={stdin_file}',
                f'--stdout={stdout_file}',
                f'--stderr={stderr_file}',
                '--run',
                '--',
                *self.lang.profile.get_exec_cmd(bin_file, args)
            ],
            privileged=True
        )
        return result

    def exec_subm(self, *, bin_file, stdin_file, stdout_file, stderr_file,
                  meta_file, limits):
        assert self.isolated
        result = yield from self._exec_in_isolate(
            bin_file=bin_file.sandbox_path,
            stdin_file=stdin_file.sandbox_path,
            stdout_file=stdout_file.sandbox_path,
            stderr_file=stderr_file.sandbox_path,
            meta_file=meta_file.container_path,  # Meta file resides in container
            limits=limits
        )
        return result

    def exec_grader(self, *, bin_file, stdout_file, test_input_file,
                    test_output_file, solution_file):
        assert not self.isolated
        result = yield from self._exec_normal(
            bin_file=bin_file.container_path,
            stdout_file=stdout_file.container_path,
            args=(
                test_input_file.container_path,
                test_output_file.container_path,
                solution_file.container_path
            )
        )
        return result


class CompileTask(Task):
    class Result(ObjectDict):
        exit_code: int
        output: str

    def __init__(self, *,
                 builder: BuilderEnviron,
                 src_file,
                 out_file):
        self.builder = builder
        self.src_file = src_file
        self.out_file = out_file

    def _run(self) -> Result:
        exit_code, output = yield from self.builder.compile(
            src_file=self.src_file,
            out_file=self.out_file
        )
        return self.Result(exit_code=exit_code, output=output)


class ExecuteResult(ObjectDict, ContextMixin):
    exec_id: int
    exit_code: int
    output: str
    meta: Optional[IsolateExecMeta]
    stdout_file: path.AFP
    stderr_file: path.AFP

    @property
    def ok(self):
        return self.exit_code == 0

    @property
    def fatal(self):
        return self.exit_code >= 2

    @property
    def timeout(self):
        if self.meta.time_wall:
            return self.meta.time_wall > self.context.judge_spec.time_limit_seconds

    @property
    def out_of_memory(self):
        if self.meta.cg_mem:
            return (self.exit_code == 1 and
                    self.meta.cg_mem >= self.context.judge_spec.mem_limit_bytes)

    @property
    def stdout(self):
        if self.stdout_file:
            with open(self.stdout_file.host_path, 'r') as f:
                return f.read()

    @property
    def stderr(self):
        if self.stderr_file:
            with open(self.stderr_file.host_path, 'r') as f:
                return f.read()


class ExecuteSubmissionTask(Task):
    def __init__(self, *,
                 sandbox: SandboxEnviron,
                 bin_file: path.AFP,
                 stdin_file: path.AFP):
        self.sandbox = sandbox
        self.bin_file = bin_file
        self.stdin_file = stdin_file

    def _run(self):
        exec_id = str(uuid.uuid4())
        stdout_file = path.AFP(path=['logs', f'{exec_id}.stdout'])
        stderr_file = path.AFP(path=['logs', f'{exec_id}.stderr'])
        meta_file = path.AFP(path=['logs', f'{exec_id}.meta'])
        result = ExecuteResult(
            exec_id=exec_id,
            stdout_file=stdout_file,
            stderr_file=stderr_file
        )

        yield ops.CheckFileExistsOp(self.stdin_file)
        yield ops.CheckFileExistsOp(self.bin_file)
        yield ops.CreateFileOp(stdout_file, mode=0o666)
        yield ops.CreateFileOp(stderr_file, mode=0o666)
        yield ops.CreateFileOp(meta_file, mode=0o666)

        exit_code, output = yield from self.sandbox.exec_subm(
            bin_file=self.bin_file,
            stdin_file=self.stdin_file,
            stdout_file=stdout_file,
            stderr_file=stderr_file,
            meta_file=meta_file,
            limits=self.sandbox.isolated and self.context.judge_spec
        )
        result.exit_code = exit_code
        result.output = output.decode('utf-8')

        if not result.is_fatal:
            meta_str = yield ops.ReadFileOp(meta_file)
            result.meta = IsolateExecMeta.parse(meta_str)

        return result


class ExecuteGraderTask(Task):
    def __init__(self, *,
                 sandbox: SandboxEnviron,
                 bin_file: path.AFP,
                 testcase_input_file: path.AFP,
                 testcase_output_file: path.AFP,
                 solution_file: path.AFP):
        self.sandbox = sandbox
        self.bin_file = bin_file
        self.testcase_input_file = testcase_input_file
        self.testcase_output_file = testcase_output_file
        self.solution_file = solution_file

    def _run(self):
        exec_id = str(uuid.uuid4())
        stdout_file = path.AFP(path=['logs', f'{exec_id}.stdout'])
        result = ExecuteResult(
            exec_id=exec_id,
            stdout_file=stdout_file,
        )

        yield ops.CheckFileExistsOp(self.bin_file)
        yield ops.CheckFileExistsOp(self.testcase_input_file)
        yield ops.CheckFileExistsOp(self.testcase_output_file)
        yield ops.CheckFileExistsOp(self.solution_file)
        yield ops.CreateFileOp(stdout_file, mode=0o666)

        exit_code, output = yield from self.sandbox.exec_grader(
            bin_file=self.bin_file,
            stdout_file=stdout_file,
            test_input_file=self.testcase_input_file,
            test_output_file=self.testcase_output_file,
            solution_file=self.solution_file
        )
        result.exit_code = exit_code
        result.output = output.decode('utf-8')

        return result

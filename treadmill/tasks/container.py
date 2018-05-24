import uuid

from docker.models.containers import Container

from treadmill.models import Lang, IsolateExecMeta
from treadmill.signal import UnsupportedLanguage, IsolateInitFail

from .base import SimpleTask, ContextTask


__all__ = [
    'BuildContext',
    'SandboxContext',
    'CompileTask',
    'ExecuteTask'
]


class BuildContext(ContextTask):
    def __init__(self, *, lang):
        self.lang = lang
        self.container_tag = self.context.config.builder_container_tag(lang)
        self.container: Container = None

    def _enter(self):
        self.container = self.context.docker_client.containers.run(
            self.container_tag,
            command='/bin/sh',
            volumes={
                self.context.host_workspace_dir: {
                    'bind': self.context.container_workspace_dir,
                    'mode': 'rw'
                }
            },
            stdin_open=True,  # keep /bin/sh alive
            remove=True,  # discard changes in image after run
            detach=True
        )

    def _exit(self):
        if self.container and self.container.status != 'end':
            self.container.kill()

    def exec(self, *commands, **kwargs):
        commands = ' '.join(commands)
        return self.container.exec_run(['/bin/sh', '-c', commands], **kwargs)


class SandboxContext(ContextTask):
    def __init__(self, *, lang, isolated):
        self.lang = lang
        self.container_tag = self.context.config.sandbox_container_tag(lang)
        self.container = None
        self.isolated = isolated

    def _enter(self):
        self.container = self.context.docker_client.containers.run(
            self.container_tag,
            command='/bin/sh',
            volumes={
                self.context.host_workspace_dir: {
                    'bind': self.context.container_workspace_dir,
                    'mode': 'rw'
                }
            },
            stdin_open=True,  # keep /bin/sh alive
            remove=True,  # discard changes in image after run
            privileged=self.isolated,  # isolate requires privileged container
            detach=True
        )
        if self.isolated:
            # Initialize isolate
            init_result = self.container.exec_run([
                'isolate',
                '--dir={d}={d}'.format(d=self.context.container_workspace_dir),
                '--init'
            ])
            if init_result.exit_code != 0:
                raise IsolateInitFail(init_result.output)

    def _exit(self):
        if self.container and self.container.status != 'end':
            self.container.kill()

    def exec(self, *commands,
             limits=None,
             meta_file=None,
             stdin_file=None,
             stdout_file=None,
             stderr_file=None,
             **kwargs):
        if self.isolated:
            assert limits is not None, 'limits must be specified when isolated'
            kwargs.update(privileged=True)
            commands = [
                'isolate',
                f'--meta={meta_file}' if meta_file else '',
                f'--mem={limits.mem_limit_bytes // 1024}',
                f'--time={limits.time_limit_seconds}',
                f'--time={limits.time_limit_seconds + 1}',
                f'--fsize={limits.file_size_limit_kilos}',
                f'--processes={limits.pid_limits}',
                f'--stdin={stdin_file}' if stdin_file else '',
                f'--stdout={stdout_file}' if stdout_file else '',
                f'--stderr={stderr_file}' if stderr_file else '',
                '--run', '--', *commands
            ]
        else:
            if stdin_file is not None:
                commands += ['<', stdin_file]
            if stdout_file is not None:
                commands += ['1>', stdout_file]
            if stderr_file is not None:
                commands += ['2>', stderr_file]

        commands = ' '.join(commands)
        return self.container.exec_run(['/bin/sh', '-c', commands], **kwargs)


class DictDecorator(dict):
    def when(self, key):
        def decorator(f):
            self[key] = f
            return f
        return decorator


class CompileTask(SimpleTask):
    _compilers = DictDecorator()

    def __init__(self, *,
                 builder: BuildContext,
                 src_file,
                 bin_file):
        self._builder = builder
        self._src_file = src_file
        self._bin_file = bin_file
        self.exit_code = None
        self.output = None

    @_compilers.when(Lang.PYTHON3)
    def noop(self):
        pass

    @_compilers.when(Lang.CPP)
    def _compile_cpp(self):
        return self._builder.exec(
            'g++', self._container_path(self._src_file),
            '-o', self._container_path(self._bin_file)
        )

    @_compilers.when(Lang.JAVA)
    def _compile_java(self):
        raise NotImplementedError()

    @_compilers.when(Lang.GO)
    def _compile_go(self):
        raise NotImplementedError()

    def _run_impl(self):
        if self._builder.lang not in self._compilers:
            raise UnsupportedLanguage(self._builder.lang.value)

        compile_fn = self._compilers.get(self._builder.lang)
        self.exit_code, self.output = compile_fn(self)


class ExecuteTask(SimpleTask):
    _executors = DictDecorator()

    def __init__(self, *,
                 sandbox: SandboxContext,
                 bin_file,
                 stdin_file):
        self._id = str(uuid.uuid4())
        self._sandbox = sandbox
        self._bin_file = bin_file
        self._stdin_file = stdin_file
        self._stdout_file = ['sandbox', 'logs', f'{self._id}.stdout']
        self._stderr_file = ['sandbox', 'logs', f'{self._id}.stderr']
        self._meta_file = ['sandbox', 'logs', f'{self._id}.meta']

        self.meta: IsolateExecMeta = None
        self.exit_code = None

    @property
    def stdout_file(self):
        return self._stdout_file

    def stdout(self):
        return self._read_host_file(self._host_path(self._stdout_file))

    def stderr(self):
        return self._read_host_file(self._host_path(self._stderr_file))

    @_executors.when(Lang.CPP)
    @_executors.when(Lang.GO)
    def _exec_native(self):
        isolated = self._sandbox.isolated
        return self._sandbox.exec(
            self._sandbox_path(self._bin_file),
            limits=self.context.judge_spec if isolated else None,
            stdin_file=self._sandbox_path(self._stdin_file),
            stdout_file=self._sandbox_path(self._stdout_file),
            stderr_file=self._sandbox_path(self._stderr_file),
            meta_file=self._sandbox_path(self._meta_file)
        )

    def _run_impl(self):
        if self._sandbox.lang not in self._executors:
            raise UnsupportedLanguage(self._sandbox.lang.value)

        assert self._host_file_exists(self._stdin_file), (
            f'"{self._host_path(self._stdin_file)}" does not exists'
        )
        assert self._host_file_exists(self._bin_file), (
            f'"{self._host_path(self._bin_file)}" does not exists'
        )
        self._create_host_file(self._stdout_file)
        self._create_host_file(self._stderr_file)
        if self._sandbox.isolated:
            self._create_host_file(self._meta_file)

        execute_fn = self._executors.get(self._sandbox.lang)
        self.exit_code, output = execute_fn(self)

        if self._sandbox.isolated and self._host_file_exists(self._meta_file):
            self.meta = IsolateExecMeta.parse(self._read_host_file(self._meta_file))


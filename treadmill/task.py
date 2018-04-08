import os
import shutil
from abc import abstractmethod

import docker
from treadmill.exception import *
from treadmill.context import JudgeContext
from treadmill.models import *
from treadmill.client import APIClient


__all__ = [
    'PrepareWorkspaceTask',
    'CleanupWorkspaceTask',
    'CompileTask',
    'SubmissionCompileTask',
    'ExecutionTask',
    'FileCompareTask'
]

ABORT = object()
CONTINUE = object()

client = docker.from_env()


def _check(cond, error_message):
    if not cond:
        raise TaskPreconditionException(error_message)


class TreadmillTask(object):
    context: JudgeContext
    api_client: APIClient

    def inject_and_run(self, context, api_client):
        self.context = context
        self.api_client = api_client
        try:
            return self.run()
        except TreadmillException as exc:
            ret = self.handle_error(exc)
            if isinstance(ret, TreadmillException):
                raise ret
            elif ret is CONTINUE:
                return
            elif ret is ABORT:
                return ABORT
            else:
                raise
        finally:
            self.cleanup()

    @abstractmethod
    def run(self):
        pass

    def cleanup(self):
        """
        Cleanup unnecessary task side effects after running. This is called
        even if running was unsuccessful and
        This is called after running the task, whether running was
        successful or not. You shouldn't raise exception inside cleanup
        since it will be called inside finally block.
        """
        pass

    def handle_error(self, exc):
        """
        Handle TreadmillError raised during run()

        Args:
            exc: raised TreadmillException

        Returns:
            `ABORT` to indicate the error is handled but needs abortion
            `None` to reraise same exception
            `TreadmillException` to transform exc
            `CONTINUE` to indicate the error is properly handled and continue
        """
        return

    @property
    def submission_src_file(self):
        """Where to place submission src file?"""
        return self.context.submission_lang_profile.src_file_name

    @property
    def submission_bin_file(self):
        """Where to place submission bin file?"""
        return self.context.submission_lang_profile.src_bin_name

    @property
    def grader_src_file(self):
        """Where to place grader src file?"""
        return os.path.basename(self.context.grader.grader_file)

    @property
    def grader_bin_file(self):
        """Where to place grader bin file?"""
        src = os.path.basename(self.context.grader.grader_file)
        return self.context.grader_lang_profile.get_bin_name(src)

    @staticmethod
    def test_input_file(testset: TestSet, testcase: TestCase):
        """Where to place testcase input file?"""
        return os.path.join('tests', str(testset.id), os.path.basename(testcase.input_file))

    @staticmethod
    def test_output_file(testset: TestSet, testcase: TestCase):
        """Where to place testcase output file?"""
        return os.path.join('tests', str(testset.id), os.path.basename(testcase.output_file))

    @property
    def host_submission_src_file(self):
        return self.context.host_path(self.submission_src_file)

    @property
    def host_submission_bin_file(self):
        return self.context.host_path(self.submission_bin_file)

    @property
    def host_grader_src_file(self):
        return self.context.host_path(self.grader_src_file)

    @property
    def host_grader_bin_file(self):
        return self.context.host_path(self.grader_bin_file)

    def host_test_input_file(self, testset: TestSet, testcase: TestCase):
        return self.context.host_path(self.test_input_file(testset, testcase))

    def host_test_output_file(self, testset: TestSet, testcase: TestCase):
        return self.context.host_path(self.test_output_file(testset, testcase))

    def read_host_file(self, rel_path):
        with open(self.context.host_path(rel_path), 'r') as f:
            return f.read()


class PrepareWorkspaceTask(TreadmillTask):
    """
    Create workspace directory in host and add symbolic links to S3 files
    """

    def run(self):
        os.makedirs(self.context.host_workspace_dir, 644, exist_ok=False)

        # prepare user source at root of workspace directory
        os.symlink(self.context.host_s3_path(self.context.submission.src_file),
                   self.host_submission_src_file)

        # prepare testcase input/output files
        for testset in self.context.judge_spec.sets:
            for testcase in testset.cases:
                os.symlink(self.context.host_s3_path(testcase.input_file),
                           self.host_test_input_file(testset, testcase))
                os.symlink(self.context.host_s3_path(testcase.output_file),
                           self.host_test_output_file(testset, testcase))

        # prepare grader source if necessary
        if self.context.grader is not None:
            os.symlink(self.context.host_s3_path(self.context.grader.grader_file),
                       self.host_grader_src_file)


class CleanupWorkspaceTask(TreadmillTask):
    def run(self):
        if (self.context.request is not None and
                os.path.isdir(self.context.host_workspace_dir)):
            shutil.rmtree(self.context.host_workspace_dir)


class FunctionRouter(dict):
    def when(self, key):
        def decorator(f):
            self[key] = f
            return f
        return decorator


class CompileTask(TreadmillTask):
    _compilers = FunctionRouter()
    _container_workspace_dir = '/workspace'
    _container = None

    def __init__(self, lang_profile, src_file, bin_file,
                 stdout_file=None, stderr_file=None):
        self._lang_profile = lang_profile
        self._src_file = src_file
        self._bin_file = bin_file
        self._stdout_file = stdout_file
        self._stderr_file = stderr_file

    def container_path(self, *args):
        return os.path.join(self._container_workspace_dir, *args)

    @_compilers.when(LanguageProfile.python3.value)
    def _skip_compile(self):
        pass

    @_compilers.when(LanguageProfile.cpp.value)
    def _compile_cpp(self):
        commands = ['g++', self.container_path(self._src_file),
                    '-o', self.container_path(self._bin_file)]
        if self._stdout_file is not None:
            commands += ['1>', self.container_path(self._stdout_file)]
        if self._stderr_file is not None:
            commands += ['2>', self.container_path(self._stderr_file)]
        commands = ' '.join(commands)

        exec_result = self._container.exec_run(['/bin/sh', '-c', commands])
        if exec_result.exit_code != 0:
            raise CodeCompileError(self.read_host_file(self._stderr_file))

    @_compilers.when(LanguageProfile.go.value)
    def _compile_go(self):
        raise NotImplementedError()

    @_compilers.when(LanguageProfile.java.value)
    def _compile_java(self):
        raise NotImplementedError()

    def run(self):
        self._container = client.containers.run(
            self.context.config.COMPILER_CONTAINER_TAG,
            command='/bin/sh',
            volumes={
                self.context.host_workspace_dir: {
                    'bind': self._container_workspace_dir,
                    'mode': 'rw'
                }
            },
            stdin_open=True,  # keep /bin/sh alive
            remove=True,
            detach=True)

        if self._lang_profile not in self._compilers:
            raise UnsupportedLanguageException(self._lang_profile)
        self._compilers[self._lang_profile](self)

    def cleanup(self):
        if self._container is not None and self._container.status != 'end':
            self._container.kill()


class SubmissionCompileTask(TreadmillTask):
    def run(self):
        task = CompileTask(
            lang_profile=self.context.submission_lang,
            src_file=self.submission_src_file,
            bin_file=self.submission_bin_file,
            stderr_file='submission_src_error.log')
        return task.inject_and_run(self.context, self.api_client)

    def handle_error(self, exc):
        if isinstance(exc, CodeCompileError):
            self.api_client.set_compile_error(self.context.request.id)
            return ABORT


class GraderCompileTask(TreadmillTask):
    def run(self):
        task = CompileTask(
            lang_profile=self.context.grader_lang,
            src_file=self.grader_src_file,
            bin_file=self.grader_bin_file,
            stderr_file='grader_src_error.log')
        return task.inject_and_run(self.context, self.api_client)

    def handle_error(self, exc):
        if isinstance(exc, CodeCompileError):
            self.api_client.set_internal_error(
                self.context.request.id,
                task=GraderCompileTask.__name__,
                error_msg=exc.message)
            return ABORT


class ExecutionTask(TreadmillTask):
    _container_workspace_dir = '/workspace'
    _executors = FunctionRouter()

    def __init__(self, lang_profile, bin_file, input_file, output_file,
                 stderr_file=None, meta_file=None, sandbox=True):
        self._lang_profile = lang_profile
        self._bin_file = bin_file
        self._input_file = input_file
        self._output_file = output_file
        self._stderr_file = stderr_file
        self._sandbox = sandbox
        self._meta_file = meta_file
        self._container = None
        self._sandbox_dir = None

    def _container_path(self, *args):
        return os.path.join(self._container_workspace_dir, *args)

    @_executors.when('cpp')
    @_executors.when('go')
    def _run_native(self):
        commands = [self._container_path(self._bin_file)]
        if self._sandbox:
            commands = self._wrap_command_with_isolate(commands)
        else:
            commands += ['1>', self._output_file,
                         '2>', self._stderr_file]
        commands = ' '.join(commands)

        exec_result = self._container.exec_run(['/bin/sh', '-c', commands])
        if exec_result.exit_code != 0:
            raise SandboxRuntimeError

    @_executors.when('python3')
    def _run_python3(self):
        raise NotImplementedError()

    @_executors.when('java')
    def _run_jre(self):
        raise NotImplementedError()

    def _wrap_command_with_isolate(self, command):
        if not isinstance(command, list):
            command = command.split()
        return [
            'isolate',
            f'--meta={self._meta_file}',
            f'--mem={self.context.judge_spec.mem_limit_bytes}',
            f'--time={self.context.judge_spec.time_limit_seconds}',
            f'--fsize={self.context.judge_spec.file_size_limit_kilos}',
            f'--processes={self.context.judge_spec.pid_limits}',
            f'--stdin={self._input_file}',
            f'--stdout={self._output_file}',
            f'--stderr={self._stderr_file}',
            '--run', '--', *command
        ]

    def _init_isolate(self):
        """Initialize isolate"""
        exec_result = self._container.exec_run([
            'isolate',
            '--dir={d}={d}'.format(d=self._container_workspace_dir),
            '--init'])
        if exec_result.exit_code != 0:
            raise IsolateInitFailError(exec_result.output)

    def run(self):
        self._container = client.containers.run(
            self.context.config.SANDBOX_CONTAINER_TAG,
            command='/bin/sh',
            volumes={
                self.context.host_workspace_dir: {
                    'bind': self._container_workspace_dir,
                    'mode': 'rw'
                }
            },
            stdin_open=True,  # keep /bin/sh alive
            remove=True,
            privileged=self._sandbox,
            detach=True)

        if self._sandbox:
            self._init_isolate()

        if self._lang_profile not in self._executors:
            raise UnsupportedLanguageException(self._lang_profile)
        self._executors[self._lang_profile](self)

    def cleanup(self):
        if self._container is not None and self._container.status != 'end':
            self._container.kill()


class SubmissionExecuteTask(TreadmillTask):
    def run(self):
        pass


class GraderExecutionTask(TreadmillTask):
    def run(self):
        pass


class FileCompareTask(TreadmillTask):
    def run(self):
        pass


class JudgeCaseTask(TreadmillTask):
    def run(self):
        """Run SubmissionExecuteTask, GraderExecuteTask, FileCompareTask"""
        pass

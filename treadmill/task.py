import os
import abc
import shutil

import docker
import treadmill.exception as exc
from treadmill.context import JudgeContext

client = docker.from_env()


def _check(cond, error_message):
    if not cond:
        raise exc.TaskPreconditionException(error_message)


class Task(object):
    @abc.abstractmethod
    def run(self, ctx: JudgeContext):
        pass

    @staticmethod
    def host_submission_src_file(ctx: JudgeContext):
        """Where to place submission src file?"""
        return ctx.get_host_workspace_path(ctx.src_lang_profile.src_file_name)

    @staticmethod
    def host_submission_bin_file(ctx: JudgeContext):
        """Where to place submission bin file?"""
        return ctx.get_host_workspace_path(ctx.src_lang_profile.src_bin_name)

    @staticmethod
    def host_grader_src_file(ctx: JudgeContext):
        """Where to place grader src file?"""
        filename = os.path.basename(ctx.judge_spec.grader.grader_file)
        return ctx.get_host_workspace_path(filename)

    @staticmethod
    def host_grader_bin_file(ctx: JudgeContext):
        """Where to place grader bin file?"""
        return ctx.grader_lang_profile.get_bin_name(Task.host_grader_src_file(ctx))


class PrepareWorkspaceTask(Task):
    """
    Create workspace directory in host and add symbolic links to S3 files
    """

    def run(self, ctx):
        os.makedirs(ctx.host_workspace_dir, 644, exist_ok=False)

        # prepare user source at root of workspace directory
        os.symlink(ctx.get_s3_path(ctx.submission.src_file),
                   self.host_submission_src_file(ctx))

        # prepare testcase input/output files
        for testset in ctx.judge_spec.sets:
            for testcase in testset.cases:
                os.symlink(ctx.get_s3_path(testcase.input_file),
                           ctx.get_host_workspace_path(str(testset.id), os.path.basename(testcase.input_file)))
                os.symlink(ctx.get_s3_path(testcase.output_file),
                           ctx.get_host_workspace_path(str(testset.id), os.path.basename(testcase.output_file)))

        # prepare grader source if necessary
        if ctx.has_grader:
            os.symlink(ctx.get_s3_path(ctx.judge_spec.grader.grader_file),
                       self.host_grader_src_file(ctx))


class CleanupWorkspaceTask(Task):
    def run(self, ctx):
        if (ctx.workspace_dir and
                os.path.isdir(ctx.host_workspace_dir)):
            shutil.rmtree(ctx.host_workspace_dir)


class FunctionRouter(dict):
    def when(self, key):
        def decorator(f):
            self[key] = f
            return f
        return decorator


class CompileTask(Task):
    __compilers = FunctionRouter()

    def __init__(self):
        self.container = None

    @__compilers.when('python3')
    def _skip_compile(self):
        pass

    @__compilers.when('cpp')
    def _compile_cpp(self):
        exec_result = self.container.exec_run(
            ['g++', *self.context.sources, '-o', self.output_path],
            stdout=False,
            stderr=True)
        if exec_result.exit_code != 0:
            raise exc.CodeCompileError(exec_result.output)

    @__compilers.when('go')
    def _compile_go(self):
        raise NotImplementedError()

    @__compilers.when('java')
    def _compile_java(self):
        raise NotImplementedError()

    def run(self, ctx):
        self.container = client.containers.run(
            self.config.COMPILER_CONTAINER_TAG,
            command='/bin/sh',
            volumes={
                self.context.workspace_dir: {
                    'bind': '/workspace',
                    'mode': 'rw'
                }
            },
            stdin_open=True,  # keep /bin/sh alive
            remove=True,
            detach=True)
        lang = ctx.src_lang_profile
        if lang not in self.__compilers:
            raise exc.UnsupportedLanguageException(lang)
        self.__compilers[lang]()

    def cleanup(self):
        if self.container is not None and self.container.status != 'end':
            self.container.kill()


class RunInSandboxTask(Task):
    __executors = FunctionRouter()

    def __init__(self, bin_file, input_files, is_sandbox=True):
        self.bin_file = bin_file
        self.input_files = input_files
        self.is_sandbox = is_sandbox
        self.container = None
        self.sandbox_root = None

    @__executors.when('cpp')
    @__executors.when('go')
    def _run_native(self, input_file, output_file):
        command = self._wrap_command_with_isolate(os.path.join('.', ))

    @__executors.when('python3')
    def _run_python3(self, input_file, output_file):
        raise NotImplementedError()

    @__executors.when('java')
    def _run_jre(self, input_file, output_file):
        raise NotImplementedError()

    @staticmethod
    def _wrap_command_with_isolate(ctx: JudgeContext, command, stdin_file, stdout_file, stderr_file):
        if not isinstance(command, list):
            command = command.split()
        return [
            'isolate',
            f'--mem={ctx.judge_spec.mem_limit_bytes}',
            f'--time={ctx.judge_spec.time_limit_seconds}',
            f'--fsize={ctx.judge_spec.file_size_limit_kilos}',
            f'--processes={ctx.judge_spec.pid_limits}',
            f'--stdin={stdin_file}',
            f'--stdout={stdout_file}',
            f'--stderr={stderr_file}',
            '--run', '--', *command
        ]

    def run(self, ctx):
        self.container = client.containers.run(
            ctx.config.SANDBOX_CONTAINER_TAG,
            command='/bin/sh',
            volumes={
                ctx.host_workspace_dir: {
                    'bind': '/workspace',
                    'mode': 'rw'
                }
            },
            stdin_open=True,  # keep /bin/sh alive
            remove=True,
            privileged=self.is_sandbox,
            detach=True)

        if self.is_sandbox:
            # initialize isolate
            isolate_init_result = self.container.exec_run(['isolate', '--init'])
            if isolate_init_result.exit_code != 0:
                raise exc.IsolateInitFailError(isolate_init_result.output)
            self.sandbox_root = isolate_init_result.output

        lang = ctx.src_lang
        if lang not in self.__executors:
            raise exc.UnsupportedLanguageException(lang)
        executor = self.__executors[lang]

        if self.is_sandbox:
            # cleanup isolate
            isolate_cleanup_result = self.container.exec_run(['isolate', '--cleanup'])


class FileCompareTask(Task):
    pass


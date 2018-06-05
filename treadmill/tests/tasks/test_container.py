from unittest.mock import Mock

import pytest

from treadmill.config import TestConfig
from treadmill.context import JudgeContextFactory, ContextMixin
from treadmill.models import Lang
from treadmill.signal import UnsupportedLanguage, IsolateInitFail
from treadmill.tasks import ops
from treadmill.tasks import path
from treadmill.tasks.container import BuilderEnviron, SandboxEnviron
from treadmill.tests import util


@pytest.fixture(scope='session')
def config():
    return TestConfig()


@pytest.fixture(scope='session')
def context_factory(config):
    return JudgeContextFactory(config)


@pytest.fixture(scope='function')
def context(context_factory):
    with context_factory.new(None):
        yield


@pytest.mark.usefixtures('context')
class TestBuilderEnviron(ContextMixin):
    def test_cpp_builder_setup_and_teardown(self,):
        builder_env = util.Wrap(BuilderEnviron(lang=Lang.CPP))
        setup_steps = builder_env.setup()

        util.assert_props(setup_steps.send(None), ops.RunDockerContainerOp,
                          container_tag=self.context.config.GCC_BUILDER_TAG)

        container = Mock()
        util.assert_finished(setup_steps, send=container)
        assert builder_env.container == container

        teardown_steps = builder_env.teardown()
        util.assert_props(teardown_steps.send(None), ops.KillDockerContainerOp,
                          container=container)

    def test_jdk_builder_setup_and_teardown(self):
        builder_env = util.Wrap(BuilderEnviron(lang=Lang.JAVA))
        setup_steps = builder_env.setup()

        util.assert_props(setup_steps.send(None), ops.RunDockerContainerOp,
                          container_tag=self.context.config.JDK_BUILDER_TAG)

        container = Mock()
        util.assert_finished(setup_steps, send=container)
        assert builder_env.container == container

        teardown_steps = builder_env.teardown()
        util.assert_props(teardown_steps.send(None), ops.KillDockerContainerOp,
                          container=container)

    def test_go_builder_setup_and_teardown(self):
        builder_env = util.Wrap(BuilderEnviron(lang=Lang.GO))
        setup_steps = builder_env.setup()

        util.assert_props(setup_steps.send(None), ops.RunDockerContainerOp,
                          container_tag=self.context.config.GO_BUILDER_TAG)

        container = Mock()
        util.assert_finished(setup_steps, send=container)
        assert builder_env.container == container

        teardown_steps = builder_env.teardown()
        util.assert_props(teardown_steps.send(None), ops.KillDockerContainerOp,
                          container=container)

    def test_setup_python_builder_fails(self):
        builder_env = util.Wrap(BuilderEnviron(lang=Lang.PYTHON3))

        with pytest.raises(UnsupportedLanguage):
            builder_env.setup([])

        builder_env.teardown([])

    def test_cpp_builder_compile(self):
        builder_env = util.Wrap(BuilderEnviron(lang=Lang.CPP))
        container = Mock()
        builder_env.setup([container])
        assert builder_env.container == container

        src_file = path.AFP(path=['foo', 'main.cpp'])
        out_file = path.AFP(path=['foo', 'main'])
        compile_steps = builder_env.compile(src_file, out_file)
        util.assert_props(compile_steps.send(None), ops.ExecInDockerContainerOp,
                          container=container,
                          cmd=['g++', '-o', '/workspace/sandbox/foo/main',
                               '/workspace/sandbox/foo/main.cpp'])

    def test_java_builder_compile(self):
        builder_env = util.Wrap(BuilderEnviron(lang=Lang.JAVA))
        container = Mock()
        builder_env.setup([container])
        assert builder_env.container == container

        src_file = path.AFP(path=['foo', 'Main.java'])
        out_file = path.AFP(path=['foo', 'Main.class'])
        compile_steps = builder_env.compile(src_file, out_file)
        util.assert_props(compile_steps.send(None), ops.ExecInDockerContainerOp,
                          container=container,
                          cmd=['javac', '-d', '/workspace/sandbox/foo',
                               '/workspace/sandbox/foo/Main.java'])

    def test_go_builder_compile(self):
        builder_env = util.Wrap(BuilderEnviron(lang=Lang.GO))
        container = Mock()
        builder_env.setup([container])
        assert builder_env.container == container

        src_file = path.AFP(path=['foo', 'main.go'])
        out_file = path.AFP(path=['foo', 'main'])
        compile_steps = builder_env.compile(src_file, out_file)
        util.assert_props(compile_steps.send(None), ops.ExecInDockerContainerOp,
                          container=container,
                          cmd=['go', 'build', '-o',
                               '/workspace/sandbox/foo/main',
                               '/workspace/sandbox/foo/main.go'])


@pytest.mark.usefixtures('context')
class TestSandboxEnviron(ContextMixin):
    @pytest.mark.parametrize('lang', [Lang.CPP, Lang.GO])
    def test_native_sandbox_setup_and_teardown(self, lang):
        sandbox_env = util.Wrap(SandboxEnviron(lang=lang, isolated=False))
        setup_steps = sandbox_env.setup()

        util.assert_props(setup_steps.send(None), ops.RunDockerContainerOp,
                          container_tag=self.context.config.NATIVE_SANDBOX_TAG)

        container = Mock()
        util.assert_finished(setup_steps, send=container)
        assert sandbox_env.container == container

        teardown_steps = sandbox_env.teardown()
        util.assert_props(teardown_steps.send(None), ops.KillDockerContainerOp,
                          container=container)

    def test_jre_sandbox_setup_and_teardown(self):
        sandbox_env = util.Wrap(SandboxEnviron(lang=Lang.JAVA, isolated=False))
        setup_steps = sandbox_env.setup()

        util.assert_props(setup_steps.send(None), ops.RunDockerContainerOp,
                          container_tag=self.context.config.JRE_SANDBOX_TAG)

        container = Mock()
        util.assert_finished(setup_steps, send=container)
        assert sandbox_env.container == container

        teardown_steps = sandbox_env.teardown()
        util.assert_props(teardown_steps.send(None), ops.KillDockerContainerOp,
                          container=container)

    def test_python_sandbox_setup_and_teardown(self):
        sandbox_env = util.Wrap(SandboxEnviron(lang=Lang.PYTHON3, isolated=False))
        setup_steps = sandbox_env.setup()

        util.assert_props(setup_steps.send(None), ops.RunDockerContainerOp,
                          container_tag=self.context.config.PY3_SANDBOX_TAG)

        container = Mock()
        util.assert_finished(setup_steps, send=container)
        assert sandbox_env.container == container

        teardown_steps = sandbox_env.teardown()
        util.assert_props(teardown_steps.send(None), ops.KillDockerContainerOp,
                          container=container)

    def test_unsupported_language_sandbox_setup_fail(self):
        sandbox_env = util.Wrap(SandboxEnviron(lang=Lang.UNKNOWN, isolated=False))
        setup_steps = sandbox_env.setup()

        with pytest.raises(UnsupportedLanguage):
            setup_steps.send(None)

        sandbox_env.teardown([])

    def test_isolated_sandbox_setup(self):
        sandbox_env = util.Wrap(SandboxEnviron(lang=Lang.CPP, isolated=True))
        setup_steps = sandbox_env.setup()

        util.assert_props(setup_steps.send(None), ops.RunDockerContainerOp,
                          container_tag=self.context.config.NATIVE_SANDBOX_TAG)

        container = Mock()
        util.assert_props(setup_steps.send(container), ops.ExecInDockerContainerOp,
                          container=container,
                          cmd=['isolate', '--dir=/workspace/sandbox=/sandbox',
                               '--init'])

        init_result = Mock(exit_code=0)
        util.assert_finished(setup_steps, send=init_result)

    def test_isolated_init_failed(self):
        sandbox_env = util.Wrap(SandboxEnviron(lang=Lang.CPP, isolated=True))
        setup_steps = sandbox_env.setup()

        util.assert_props(setup_steps.send(None), ops.RunDockerContainerOp,
                          container_tag=self.context.config.NATIVE_SANDBOX_TAG)

        container = Mock()
        util.assert_props(setup_steps.send(container), ops.ExecInDockerContainerOp,
                          container=container,
                          cmd=['isolate', '--dir=/workspace/sandbox=/sandbox',
                               '--init'])

        init_result = Mock(exit_code=1)
        with pytest.raises(IsolateInitFail):
            util.assert_finished(setup_steps, send=init_result)

    def test_native_exec(self):
        sandbox_env = util.Wrap(SandboxEnviron(lang=Lang.CPP, isolated=False))
        container = Mock()
        sandbox_env.setup([container])

        bin_file = path.AFP(path=['foo', 'main'])
        stdin_file = path.AFP(path=['bar', 'input.txt'])
        stdout_file = path.AFP(path=['bar', 'output.txt'])
        exec_steps = sandbox_env.exec(
            bin_file=bin_file,
            stdin_file=stdin_file,
            stdout_file=stdout_file
        )

        util.assert_props(exec_steps.send(None), ops.ExecInDockerContainerOp,
                          container=container,
                          cmd=['/workspace/sandbox/foo/main',
                               '<', '/workspace/sandbox/bar/input.txt',
                               '1>', '/workspace/sandbox/bar/output.txt'],
                          kwargs={'privileged': False})

        exec_result = Mock(exit_code=0)
        util.assert_finished(exec_steps, send=exec_result)

    def test_native_isolated_exec(self):
        sandbox_env = util.Wrap(SandboxEnviron(lang=Lang.CPP, isolated=True))
        container = Mock()
        isolate_init_result = Mock(exit_code=0)
        sandbox_env.setup([container, isolate_init_result])

        bin_file = path.AFP(path=['foo', 'main'])
        stdin_file = path.AFP(path=['bar', 'input.txt'])
        stdout_file = path.AFP(path=['bar', 'output.txt'])
        stderr_file = path.AFP(path=['bar', 'stderr.txt'])
        meta_file = path.AFP(path=['bar', 'meta.txt'])
        limits = Mock(
            mem_limit_bytes=1024*1024*256,
            time_limit_seconds=5.0,
            file_size_limit_kilos=0,
            pid_limits=1
        )

        exec_steps = sandbox_env.exec(
            bin_file=bin_file,
            stdin_file=stdin_file,
            stdout_file=stdout_file,
            stderr_file=stderr_file,
            meta_file=meta_file,
            limits=limits
        )

        util.assert_props(exec_steps.send(None), ops.ExecInDockerContainerOp,
                          container=container,
                          cmd=['isolate',
                               '--meta=/sandbox/bar/meta.txt',
                               '--mem=262144',
                               '--time=5.0',
                               '--wall-time=15.0',
                               '--extra-time=1.0',
                               '--fsize=0',
                               '--processes=1',
                               '--stdin=/sandbox/bar/input.txt',
                               '--stdout=/sandbox/bar/output.txt',
                               '--stderr=/sandbox/bar/stderr.txt',
                               '--run',
                               '--',
                               '/sandbox/foo/main'],
                          kwargs={'privileged': True})

        exec_result = Mock(exit_code=0)
        util.assert_finished(exec_steps, send=exec_result)

    def test_java_exec(self):
        sandbox_env = util.Wrap(SandboxEnviron(lang=Lang.JAVA, isolated=False))
        container = Mock()
        sandbox_env.setup([container])

        bin_file = path.AFP(path=['foo', 'Main.class'])
        stdin_file = path.AFP(path=['bar', 'input.txt'])
        stdout_file = path.AFP(path=['bar', 'output.txt'])
        exec_steps = sandbox_env.exec(
            bin_file=bin_file,
            stdin_file=stdin_file,
            stdout_file=stdout_file
        )

        util.assert_props(exec_steps.send(None), ops.ExecInDockerContainerOp,
                          cmd=['java', '/workspace/sandbox/foo/Main.class',
                               '<', '/workspace/sandbox/bar/input.txt',
                               '1>', '/workspace/sandbox/bar/output.txt'],
                          kwargs={'privileged': False})

        exec_result = Mock(exit_code=0)
        util.assert_finished(exec_steps, send=exec_result)

    def test_python_exec(self):
        sandbox_env = util.Wrap(SandboxEnviron(lang=Lang.PYTHON3, isolated=False))
        container = Mock()
        sandbox_env.setup([container])

        bin_file = path.AFP(path=['foo', 'main.py'])
        stdin_file = path.AFP(path=['bar', 'input.txt'])
        stdout_file = path.AFP(path=['bar', 'output.txt'])
        exec_steps = sandbox_env.exec(
            bin_file=bin_file,
            stdin_file=stdin_file,
            stdout_file=stdout_file
        )

        util.assert_props(exec_steps.send(None), ops.ExecInDockerContainerOp,
                          cmd=['python', '/workspace/sandbox/foo/main.py',
                               '<', '/workspace/sandbox/bar/input.txt',
                               '1>', '/workspace/sandbox/bar/output.txt'],
                          kwargs={'privileged': False})

        exec_result = Mock(exit_code=0)
        util.assert_finished(exec_steps, send=exec_result)

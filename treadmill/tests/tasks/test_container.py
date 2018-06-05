from unittest.mock import Mock

import pytest

from treadmill.config import TestConfig
from treadmill.context import JudgeContextFactory, ContextMixin
from treadmill.models import Lang
from treadmill.signal import UnsupportedLanguage
from treadmill.tasks import ops
from treadmill.tasks import path
from treadmill.tasks.container import BuilderEnviron
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

    def test_setup_go_builder_setup_and_teardown(self):
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

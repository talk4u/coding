import contextlib
import os
from abc import abstractmethod

from treadmill.context import JudgeContext
from treadmill.models import TestSet, TestCase


class PathMixin(object):
    context: JudgeContext

    @property
    def _subm_src_file(self):
        return ['sandbox', self.context.subm_lang.profile.src_file_name]

    @property
    def _subm_bin_file(self):
        return ['sandbox', self.context.subm_lang.profile.bin_file_name]

    @property
    def _grader_src_file(self):
        return ['sandbox', self.context.subm_lang.profile.bin_file_name]

    @property
    def _grader_bin_file(self):
        return ['sandbox', self.context.grader_lang.profile.bin_file_name]

    @staticmethod
    def _test_input_file(testset: TestSet, testcase: TestCase):
        return ['sandbox', str(testset.id), os.path.basename(testcase.input_file)]

    @staticmethod
    def _test_output_file(testset: TestSet, testcase: TestCase):
        return ['answer', str(testset.id), os.path.basename(testcase.output_file)]

    def _create_host_file(self, path, mode=None):
        open(self.context.host_path(path), 'a').close()
        if mode:
            os.chmod(self.context.host_path(path), mode)

    def _read_host_file(self, path):
        with open(self.context.host_path(path), 'r') as f:
            return f.read()

    def _host_file_exists(self, path):
        return os.path.exists(self.context.host_path(path))


class SimpleTask(PathMixin):
    context: JudgeContext

    def run(self, context):
        self.context = context
        self._run_impl()
        return self

    @abstractmethod
    def _run_impl(self):
        pass


class ContextTask(PathMixin):
    context: JudgeContext

    @contextlib.contextmanager
    def run(self, context):
        self.context = context
        self._enter()
        yield self
        self._exit()

    @abstractmethod
    def _enter(self):
        pass

    @abstractmethod
    def _exit(self):
        pass

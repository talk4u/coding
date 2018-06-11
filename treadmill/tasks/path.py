import os
from typing import List

from treadmill.context import get_current_context, ContextMixin


class AFP(ContextMixin):
    """
    Abstract File Path

    Since host, docker container, and isolate sandbox all shares the
    same directory (workspace) AFP defines the shared abstract file
    location which can be evaluated to raw path any time.
    """
    container_root = '/workspace'
    sandbox_root = '/sandbox'
    sandbox_prefix = os.path.relpath(sandbox_root, '/')

    def __init__(self, *, path: List[str], sandbox_visible=True, s3fs_path=None):
        """
        Args:
            path: List of path segments
            sandbox_visible: Whether the file is visible in isolated sandbox
        """

        self._path = path
        self._sandbox_visible = sandbox_visible
        self._s3fs_path = s3fs_path

    @property
    def host_path(self):
        return os.path.join(
            self.context.config.HOST_WORKSPACE_ROOT,
            str(self.context.request.id),
            self.sandbox_prefix if self._sandbox_visible else '',
            *self._path
        )

    @property
    def s3fs_path(self):
        if self._s3fs_path:
            return os.path.join(
                self.context.config.S3FS_ROOT,
                *self._s3fs_path
            )

    @property
    def container_path(self):
        return os.path.join(
            self.container_root,
            self.sandbox_prefix if self._sandbox_visible else '',
            *self._path
        )

    @property
    def sandbox_path(self):
        return os.path.join(self.sandbox_root, *self._path)

    def __repr__(self):
        if self is ROOT:
            return 'ROOT'
        elif self is SANDBOX_ROOT:
            return 'SANDBOX_ROOT'
        return repr(self._path)


ROOT = AFP(path=[], sandbox_visible=False)
SANDBOX_ROOT = AFP(path=[], sandbox_visible=True)


def subm_src_file():
    context = get_current_context()
    return AFP(path=['subm', context.subm_lang.profile.src_file_name],
               s3fs_path=[context.submission.src_file])


def subm_bin_file():
    bin_file_name = get_current_context().subm_lang.profile.bin_file_name
    return AFP(path=['subm', bin_file_name])


def grader_src_file():
    context = get_current_context()
    return AFP(path=['grader', context.grader_lang.profile.src_file_name],
               s3fs_path=[context.grader.src_file])


def grader_bin_file():
    bin_file_name = get_current_context().grader_lang.profile.bin_file_name
    return AFP(path=['grader', bin_file_name])


def test_input_file(testset, testcase):
    return AFP(path=['data', str(testset.id), os.path.basename(testcase.input_file)],
               s3fs_path=[testcase.input_file])


def test_output_file(testset, testcase):
    return AFP(path=['data', str(testset.id), os.path.basename(testcase.output_file)],
               s3fs_path=[testcase.output_file],
               sandbox_visible=False)

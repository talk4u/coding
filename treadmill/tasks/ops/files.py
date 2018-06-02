import filecmp
import os
import shutil

from treadmill.tasks.ops.base import Operation
from treadmill.tasks.path import AFP


__all__ = [
    'CheckFileExistsOp',
    'CreateFileOp',
    'MakeDirectoryOp',
    'CreateSymlinkOp',
    'ReadFileOp',
    'CompareFileOp',
    'RemoveDirectoryOp'
]


class CheckFileExistsOp(Operation):
    def __init__(self, afp: AFP):
        self.afp = afp

    def _run(self):
        assert os.path.exists(self.afp.host_path), (
            f'File {self.afp.host_path} does not exists'
        )


class CreateFileOp(Operation):
    def __init__(self, afp: AFP, mode=None):
        self.afp = afp
        self.mode = mode

    def _run(self):
        open(self.afp.host_path, 'a').close()
        if self.mode:
            os.chmod(self.afp.host_path, self.mode)


class MakeDirectoryOp(Operation):
    def __init__(self, afp: AFP, mode=None, exist_ok=False):
        self.afp = afp
        self.mode = mode
        self.exist_ok = exist_ok

    def _run(self):
        os.makedirs(self.afp.host_path, mode=self.mode, exist_ok=self.exist_ok)


class CreateSymlinkOp(Operation):
    def __init__(self, src_path: str, dest_path: str):
        self.src_path = src_path
        self.dest_path = dest_path

    def _run(self):
        os.symlink(self.src_path, self.dest_path)


class ReadFileOp(Operation):
    def __init__(self, afp):
        self.afp = afp

    def _run(self):
        with open(self.afp.host_path, 'r') as f:
            return f.read()


class CompareFileOp(Operation):
    def __init__(self, target: AFP, expected: AFP):
        self.target = target
        self.expected = expected

    def _run(self):
        return filecmp.cmp(
            self.target.host_path,
            self.expected.host_path,
            shallow=False
        )


class RemoveDirectoryOp(Operation):
    def __init__(self, target: AFP):
        self.target = target

    def _run(self):
        if os.path.isdir(self.target.host_path):
            shutil.rmtree(self.target.host_path)

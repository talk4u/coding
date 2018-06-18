import filecmp
import os
import shutil

from treadmill.tasks.base import Task
from treadmill.tasks.path import AFP


__all__ = [
    'CheckFileExistsOp',
    'CreateFileOp',
    'MakeDirectoryOp',
    'CopyFileOp',
    'ReadFileOp',
    'CompareFileOp',
    'RemoveDirectoryOp'
]


class CheckFileExistsOp(Task):
    def __init__(self, afp: AFP):
        self.afp = afp

    def _run(self):
        assert os.path.exists(self.afp.host_path), (
            f'File {self.afp.host_path} does not exists'
        )


class CreateFileOp(Task):
    def __init__(self, afp: AFP, mode=None):
        self.afp = afp
        self.mode = mode

    def _run(self):
        dest_dir = os.path.dirname(self.afp.host_path)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir, mode=0o755)
        open(self.afp.host_path, 'a').close()
        if self.mode:
            os.chmod(self.afp.host_path, self.mode)


class MakeDirectoryOp(Task):
    def __init__(self, afp: AFP, mode=0o755, exist_ok=False):
        self.afp = afp
        self.mode = mode
        self.exist_ok = exist_ok

    def _run(self):
        os.makedirs(self.afp.host_path, mode=self.mode, exist_ok=self.exist_ok)


class CopyFileOp(Task):
    def __init__(self, src_path: str, dest_path: str):
        self.src_path = src_path
        self.dest_path = dest_path

    def _run(self):
        dest_dir = os.path.dirname(self.dest_path)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir, mode=0o755)
        shutil.copyfile(self.src_path, self.dest_path)


class ReadFileOp(Task):
    def __init__(self, afp):
        self.afp = afp

    def _run(self):
        with open(self.afp.host_path, 'r') as f:
            return f.read()


class CompareFileOp(Task):
    def __init__(self, target: AFP, expected: AFP):
        self.target = target
        self.expected = expected

    def _run(self):
        a = open(self.target.host_path, 'r').read().strip()
        b = open(self.expected.host_path, 'r').read().strip()
        return a == b


class RemoveDirectoryOp(Task):
    def __init__(self, target: AFP):
        self.target = target

    def _run(self):
        if os.path.isdir(self.target.host_path):
            shutil.rmtree(self.target.host_path)

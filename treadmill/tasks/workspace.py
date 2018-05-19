import os
import shutil

from .base import ContextTask


__all__ = [
    'WorkspaceContext'
]


class WorkspaceContext(ContextTask):
    def _enter(self):
        os.makedirs(self.context.host_workspace_dir, 644, exist_ok=False)

        os.symlink(self._s3fs_path(self.context.submission.src_file),
                   self._host_path(self._subm_src_file))

        for testset in self.context.judge_spec.testsets:
            for testcase in testset.cases:
                os.symlink(self._s3fs_path(testcase.input_file),
                           self._host_path(self._test_input_file(testset, testcase)))
                os.symlink(self._s3fs_path(testcase.output_file),
                           self._host_path(self._test_output_file(testset, testcase)))

        if self.context.grader:
            os.symlink(self._s3fs_path(self.context.judge_spec.grader.grader_file),
                       self._host_path(self._grader_src_file))

    def _exit(self):
        if self.context.request and os.path.isdir(self.context.host_workspace_dir):
            shutil.rmtree(self.context.host_workspace_dir)

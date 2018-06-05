from .base import Environ
from . import ops
from . import path


__all__ = [
    'WorkspaceEnviron'
]


class WorkspaceEnviron(Environ):
    def _setup(self):
        yield ops.MakeDirectoryOp(path.ROOT, mode=644)

        subm_src_file = path.subm_src_file()
        yield ops.CreateSymlinkOp(
            src_path=subm_src_file.s3fs_path,
            dest_path=subm_src_file.host_path
        )

        for testset in self.context.judge_spec.testsets:
            for testcase in testset.testcases:
                test_input_file = path.test_input_file(testset, testcase)
                yield ops.CreateSymlinkOp(
                    src_path=test_input_file.s3fs_path,
                    dest_path=test_input_file.host_path
                )

                test_output_file = path.test_output_file(testset, testcase)
                yield ops.CreateSymlinkOp(
                    src_path=test_output_file.s3fs_path,
                    dest_path=test_output_file.host_path
                )

        if self.context.grader:
            grader_src_file = path.grader_src_file()
            yield ops.CreateSymlinkOp(
                src_path=grader_src_file.s3fs_path,
                dest_path=grader_src_file.host_path
            )

    def _teardown(self):
        yield ops.RemoveDirectoryOp(path.ROOT)

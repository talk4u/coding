import filecmp

from .base import SimpleTask
from .container import *

__all__ = [
    'JudgeTestSetTask'
]


class JudgeTestSetTask(SimpleTask):
    def __init__(self, subm_sandbox, grader_sandbox, testset):
        self._subm_sandbox: SandboxContext = subm_sandbox
        self._grader_sandbox: SandboxContext = grader_sandbox
        self.testset = testset

    def _run_impl(self):
        for testcase in self.testset.cases:
            input_file = self._test_input_file(self.testset, testcase)
            expected_file = self._host_path(self._test_output_file(self.testset, testcase))

            result = ExecuteTask(
                sandbox=self._subm_sandbox,
                stdin_file=input_file,
                bin_file=self._subm_bin_file
            ).run(self.context)

            if self._grader_sandbox:
                result = ExecuteTask(
                    sandbox=self._grader_sandbox,
                    stdin_file=result.stdout_file,
                    bin_file=self._grader_bin_file
                ).run(self.context)

            output_file = self._host_path(result.stdout_file)

            passed = filecmp.cmp(output_file, expected_file, shallow=False)

            if passed:
                self.context.api_client.set_passed(
                    self.context.request.id,
                    self.testset.id,
                    testcase.id
                )
            else:
                self.context.api_client.set_wrong_answer(
                    self.context.request.id,
                    self.testset.id,
                    testcase.id
                )
                break

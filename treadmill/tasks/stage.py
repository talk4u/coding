from contextlib import ExitStack

from treadmill.signal import SubmissionCompileError, GraderCompileError
from treadmill.tasks.judge import JudgeTask

from .base import Task
from .container import BuilderEnviron, CompileTask, SandboxEnviron
from . import path


__all__ = [
    'CompileStage',
    'JudgeStage'
]


class CompileStage(Task):
    def _run(self):
        subm_lang = self.context.subm_lang
        if subm_lang.profile.need_compile:
            with BuilderEnviron(lang=self.context.subm_lang) as subm_builder:
                yield from self._build_subm(subm_builder)
                if self.context.grader and self.context.subm_lang == self.context.grader_lang:
                    yield from self._build_grader(subm_builder)
                    return

        if self.context.grader:
            grader_lang = self.context.grader_lang
            if grader_lang.profile.need_compile:
                with BuilderEnviron(lang=self.context.grader_lang) as grader_builder:
                    yield from self._build_grader(grader_builder)

    @staticmethod
    def _build_subm(builder):
        result = yield CompileTask(
            builder=builder,
            src_file=path.subm_src_file(),
            out_file=path.subm_bin_file()
        )
        if result.exit_code != 0:
            raise SubmissionCompileError(result.output)

    @staticmethod
    def _build_grader(builder):
        result = yield CompileTask(
            builder=builder,
            src_file=path.grader_src_file(),
            out_file=path.grader_bin_file()
        )
        if result.exit_code != 0:
            raise GraderCompileError(result.output)


class JudgeStage(Task):
    def _run(self):
        with ExitStack() as stack:
            subm_sandbox = SandboxEnviron(lang=self.context.subm_lang, isolated=True)
            stack.enter_context(subm_sandbox)
            grader_sandbox = None
            if self.context.grader:
                grader_sandbox = SandboxEnviron(lang=self.context.grader_lang, isolated=False)
                stack.enter_context(grader_sandbox)

            yield JudgeTask(
                subm_sandbox=subm_sandbox,
                grader_sandbox=grader_sandbox
            )

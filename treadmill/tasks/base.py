import contextlib
import inspect
import logging
import threading
from abc import abstractmethod

from treadmill.context import ContextMixin
from treadmill.utils import ReprMixin
from .logger import IndentLogger

__all__ = [
    'Task',
    'Environ',
    'push_environ',
    'pop_environ',
    'get_active_environs',
    'get_task_stack'
]


_logger: IndentLogger = logging.getLogger('treadmill.tasks')
_logger.set_indent_provider(lambda: 2 * len(_global_task.stack) * ' ')


def runnable(f):
    return hasattr(f, 'run') and callable(f.run)


def run_generator_function_or_callable(f):
    if inspect.isgeneratorfunction(f):
        gen = f()
        subtask_result = None
        while True:
            try:
                subtask = gen.send(subtask_result)
                subtask_result = subtask.run() if runnable(subtask) else None
            except StopIteration as end:
                return end.value
    elif callable(f):
        return f()


_global_task = threading.local()
_global_task.stack = []


@contextlib.contextmanager
def set_current_task(task):
    _global_task.stack.append(task)
    _logger.debug_with_indent(task)
    yield task
    _global_task.stack.pop()


def get_task_stack():
    return [str(task) for task in _global_task.stack]


class Task(ContextMixin, ReprMixin):
    def run(self):
        with set_current_task(self):
            return run_generator_function_or_callable(self._run)

    @abstractmethod
    def _run(self):
        pass


_global_environs = threading.local()
_global_environs.stack = []


def push_environ(env):
    _global_environs.stack.append(env)
    _global_task.stack.append(env)
    _logger.debug_with_indent(env)


def pop_environ():
    _global_environs.stack.pop()
    _global_task.stack.pop()


def get_active_environs():
    global _global_environs
    return list(_global_environs.stack)


class Environ(ContextMixin, ReprMixin):
    def __enter__(self):
        push_environ(self)
        try:
            run_generator_function_or_callable(self._setup)
            return self
        except Exception:
            pop_environ()
            run_generator_function_or_callable(self._teardown)
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        pop_environ()
        run_generator_function_or_callable(self._teardown)
        return exc_type is None

    @abstractmethod
    def _setup(self):
        pass

    @abstractmethod
    def _teardown(self):
        pass

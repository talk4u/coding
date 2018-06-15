import contextlib
import inspect
import logging
import threading
from abc import abstractmethod

from dramatiq.middleware import TimeLimitExceeded

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
        task_gen = f()
        subtask_result = None
        subtask_error = False
        while True:
            try:
                subtask = task_gen.send(subtask_result)
                if runnable(subtask):
                    try:
                        subtask_result = subtask.run()
                    except Exception as e:
                        subtask_error = True
                        task_gen.throw(e)
                else:
                    subtask_result = None
            except StopIteration as end:
                return end.value
            except (TimeLimitExceeded, KeyboardInterrupt) as e:
                if not subtask_error:
                    task_gen.throw(e)
                raise
    elif callable(f):
        return f()


_global_task = threading.local()
_global_task.stack = []


@contextlib.contextmanager
def set_current_task(task):
    _global_task.stack.append(task)
    _logger.debug_with_indent(task)
    try:
        yield task
    finally:
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
        except BaseException:
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

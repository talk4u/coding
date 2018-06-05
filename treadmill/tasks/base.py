import inspect
import threading
from abc import abstractmethod

from treadmill.context import ContextMixin


__all__ = [
    'Task',
    'Environ',
    'push_environ',
    'pop_environ',
    'get_active_environs'
]


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


class Task(ContextMixin):
    def run(self):
        run_generator_function_or_callable(self._run)

    @abstractmethod
    def _run(self):
        pass

    def __repr__(self):
        return repr(self.__dict__)


global_environs = threading.local()


def push_environ(env):
    global global_environs
    stack = global_environs.stack or []
    stack.append(env)
    global_environs.stack = stack


def pop_environ():
    global global_environs
    stack = global_environs.stack
    if stack:
        ret = stack.pop()
        global_environs.stack = stack or None
        return ret


def get_active_environs():
    global global_environs
    return list(global_environs.stack)


class Environ(ContextMixin):
    def __enter__(self):
        push_environ(self)
        run_generator_function_or_callable(self._setup)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pop_environ()
        run_generator_function_or_callable(self._teardown)

    @abstractmethod
    def _setup(self):
        pass

    @abstractmethod
    def _teardown(self):
        pass

    def __repr__(self):
        return repr(self.__dict__)

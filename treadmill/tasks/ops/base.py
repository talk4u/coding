from abc import abstractmethod

from treadmill.context import ContextMixin


class Operation(ContextMixin):
    def run(self):
        return self._run()

    @abstractmethod
    def _run(self):
        pass

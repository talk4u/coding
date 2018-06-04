from abc import abstractmethod

from treadmill.context import ContextMixin


class Operation(ContextMixin):
    def run(self):
        return self._run()

    @abstractmethod
    def _run(self):
        pass

    def __repr__(self):
        return repr(self.__dict__)

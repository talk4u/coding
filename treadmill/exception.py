class TreadmillException(Exception):
    """Base Exception class for Treadmill"""
    pass


class TaskException(TreadmillException):
    message: str


class CodeCompileError(TaskException):
    def __init__(self, message):
        self.message = message


class IsolateInitFailError(TaskException):
    def __init__(self, message):
        self.message = message


class SandboxRuntimeError(TaskException):
    def __init__(self, message):
        self.message = message


class TaskPreconditionException(TaskException):
    def __init__(self, message):
        self.message = message


class UnsupportedLanguageException(TaskException):
    def __init__(self, lang):
        self.message = 'Unsupported language: {}'.format(lang)

class TException(Exception):
    """Base Exception class for Treadmill"""
    pass


class TaskException(TException):
    pass


class CodeCompileError(TaskException):
    def __init__(self, message):
        self.message = message


class IsolateInitFailError(TaskException):
    def __init__(self, message):
        self.message = message


class TaskPreconditionException(TException):
    def __init__(self, message):
        self.message = message


class UnsupportedLanguageException(TaskException):
    def __init__(self, lang):
        self.message = 'Unsupported language: {}'.format(lang)

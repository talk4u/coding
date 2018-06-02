class TreadmillSignal(Exception):
    message = None
    retryable = False
    api_server_reachable = True

    def __init__(self, message=None):
        if message:
            self.message = message

    def __str__(self):
        return f'{type(self)}: {self.message}'


# =========================================================
# Temporary errors (retry works)
# =========================================================

class InternalApiError(TreadmillSignal):
    retryable = True
    api_server_reachable = False
    """ Main API server is down or some error has occurred """
    pass


# =========================================================
# Server fault signals
# =========================================================

class ServerFault(TreadmillSignal):
    message = 'Internal error has occurred'


class IsolateInitFail(ServerFault):
    message = 'Failed to initialize isolate'


class UnsupportedLanguage(ServerFault):
    def __init__(self, lang):
        self.message = f'Unsupported language {lang}'


class IsolateExecutionError(ServerFault):
    pass


class GraderCompileError(ServerFault):
    pass


class GraderRuntimeError(ServerFault):
    pass


# =========================================================
# User fault signals
# =========================================================

class UserFault(TreadmillSignal):
    pass


class SubmissionCompileError(UserFault):
    pass


class OutOfMemory(UserFault):
    pass


class Timeout(UserFault):
    pass


class SubmissionRuntimeError(UserFault):
    pass


class WrongAnswer(UserFault):
    pass

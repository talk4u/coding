class TreadmillSignal(Exception):
    message = None


# =========================================================
# Server fault signals
# =========================================================

class ServerFault(TreadmillSignal):
    pass


class JudgeRequestNotFound(ServerFault):
    pass


class IsolateInitFail(ServerFault):
    pass


class GraderCompileError(ServerFault):
    def __init__(self, error):
        self.message = error


class GraderRuntimeError(ServerFault):
    def __init__(self, error):
        self.message = error


# =========================================================
# User fault signals
# =========================================================

class UserFault(TreadmillSignal):
    pass


class UnsupportedLanguage(ServerFault):
    def __init__(self, lang):
        self.message = f'Unsupported language {lang}'


class SubmissionCompileError(UserFault):
    def __init__(self, error):
        self.message = error


class OutOfMemory(UserFault):
    pass


class Timeout(UserFault):
    pass


class SubmissionRuntimeError(UserFault):
    pass


class WrongAnswer(UserFault):
    pass

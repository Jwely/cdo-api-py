
class AuthError(Exception):
    pass


class BadExtentError(Exception):
    pass


class InvalidEndpoint(Exception):
    pass


class InvalidDatestring(Exception):
    pass


class RequiredArgumentError(Exception):
    pass


class Request429Error(Exception):
    pass


class RequestsPerSecondLimitExceeded(Request429Error):
    pass


class RequestsPerDayLimitExceeded(Request429Error):
    pass


class Request400Error(Exception):
    pass
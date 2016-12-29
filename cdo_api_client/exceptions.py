
class AuthError(Exception):
    pass


class InvalidEndpoint(Exception):
    pass


class RequiredArgumentError(Exception):
    pass


class Request429Error(Exception):
    pass


class RequestsPerSecondLimitExceeded(Request429Error):
    pass


class RequestsPerDayLimitExceeded(Request429Error):
    pass
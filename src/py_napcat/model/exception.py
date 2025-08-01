class CustomError(BaseException):
    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

    def __str__(self):
        return self.message


class ParameterError(CustomError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class SendElementOnlyError(CustomError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class ParseError(CustomError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class EventReceivedOnlyError(CustomError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class UnregisteredError(CustomError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class UnregisteredEventError(UnregisteredError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class UnregisteredElementError(UnregisteredError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class ParserRegisteredError(CustomError):
    def __init__(self, message: str) -> None:
        super().__init__(message)

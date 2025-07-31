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

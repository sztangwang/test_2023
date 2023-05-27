

class BaseError(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, message=""):
        self.message = message

    def __repr__(self):
        return repr(self.message)


class FileNotExistError(BaseError):
    """Image does not exist."""


class InvalidMatchingMethodError(BaseError):
    """
        This is InvalidMatchingMethodError BaseError
        When an invalid matching method is used in settings.
    """
    pass


class AirtestError(BaseError):
    """
        This is Airtest BaseError
    """
    pass


class TargetNotFoundError(AirtestError):
    """
        This is TargetNotFoundError BaseError
        When something is not found
    """
    pass

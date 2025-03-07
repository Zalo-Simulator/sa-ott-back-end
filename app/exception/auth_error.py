from http import HTTPStatus

from app.exception.base_error import BaseError


class AuthenticationError(BaseError):
    INVALID_USER_LOGIN = BaseError(
        status=HTTPStatus.UNAUTHORIZED,
        code=1000,
        message="Incorrect password",
    )
    
    INACTIVE_USER = BaseError(
        status=HTTPStatus.UNAUTHORIZED,
        code=1001,
        message="Inactive user",
    )
    CANNOT_REGISTER_ACCOUNT = BaseError(
        status=HTTPStatus.UNAUTHORIZED,
        code=1002,
        message="Cannot register account",
    )
    PERMISSION_DENIED = BaseError(
        status=HTTPStatus.UNAUTHORIZED,
        code=1003,
        message="Permission denied",
    )
    INVALID_CREDENTIALS = BaseError(
        status=HTTPStatus.UNAUTHORIZED,
        code=1004,
        message="Invalid credentials",
    )
    EMAIL_ALREADY_EXIST = BaseError(
        status=HTTPStatus.BAD_REQUEST,
        code=1005,
        message="Email already exist",
    )
    PHONE_ALREADY_EXIST = BaseError(
        status=HTTPStatus.BAD_REQUEST,
        code=1005,
        message="Phone already exist",
    )
    USER_NOT_FOUND = BaseError(
        status=HTTPStatus.NOT_FOUND,
        code=1006,
        message="User not found",
    )

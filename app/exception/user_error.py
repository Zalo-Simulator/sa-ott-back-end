from http import HTTPStatus

from exception.base_error import BaseError


class UserError(BaseError):
    CANNOT_CREATE_USER = BaseError(
        status=HTTPStatus.BAD_REQUEST,
        code=1100,
        message="Cannot create user",
    )
    CANNOT_UPDATE_USER_ACCOUNT = BaseError(
        status=HTTPStatus.BAD_REQUEST,
        code=1101,
        message="Cannot update user account",
    )
    CANNOT_GET_USER_DETAIL = BaseError(
        status=HTTPStatus.BAD_REQUEST,
        code=1102,
        message="Cannot get user detail",
    )

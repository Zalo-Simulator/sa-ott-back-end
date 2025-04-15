from http import HTTPStatus

from app.exception.base_error import BaseError


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

    CANNOT_GET_USER = BaseError(
        status=HTTPStatus.BAD_REQUEST,
        code=1102,
        message="Cannot get user",
    )

    CANNOT_ADD_CONTACT = BaseError(
        status=HTTPStatus.BAD_REQUEST,
        code=1103,
        message="Cannot add contact",
    )
    CANNOT_GET_USER_PENDING_CONTACTS = BaseError(
        status=HTTPStatus.BAD_REQUEST,
        code=1104,
        message="Cannot get user pending contacts",
    )
    CANNOT_GET_USER_CONTACTS = BaseError(
        status=HTTPStatus.BAD_REQUEST,
        code=1105,
        message="Cannot get user contacts",
    )

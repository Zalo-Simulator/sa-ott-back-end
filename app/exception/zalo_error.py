"""One for all Zalo errors"""

from http import HTTPStatus

from app.exception.base_error import BaseError


class ZaloError(BaseError):
    INTERNAL_SERVER_ERROR = BaseError(
        status=HTTPStatus.INTERNAL_SERVER_ERROR,
        code=1000,
        message="The server cannot process the request for an unknown reason",
    )
    GET_PAYLOAD_PROPERTY_FAILED = BaseError(
        status=HTTPStatus.BAD_REQUEST,
        code=2500,
        message="Get payload's property failed",
    )
    CANNOT_UPLOAD_FILE = BaseError(
        status=HTTPStatus.BAD_REQUEST,
        code=2501,
        message="Cannot upload file",
    )
    CANNOT_DOWNLOAD_FILE = BaseError(
        status=HTTPStatus.BAD_REQUEST,
        code=2502,
        message="Cannot download file",
    )
    GROUP_NOT_FOUND = BaseError(
        status=HTTPStatus.NOT_FOUND,
        code=2503,
        message="Group not found",
    )

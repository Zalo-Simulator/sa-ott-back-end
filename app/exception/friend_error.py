from app.exception.base_error import BaseError
from http import HTTPStatus

class FriendError(BaseError):

    CANNOT_GET_FRIEND_DETAIL = BaseError(
        status=HTTPStatus.BAD_REQUEST,
        code=1200,
        message="Cannot get friend detail",
    )

    CANNOT_GET_FRIEND_LIST = BaseError(
        status=HTTPStatus.BAD_REQUEST,
        code=1200,
        message="Cannot get friend list",
    )

    CANNOT_CREATE_FRIEND_REQUEST = BaseError(
        status=HTTPStatus.BAD_REQUEST,
        code=1201,
        message="Cannot create friend request",
    )

    CANNOT_UPDATE_FRIEND_REQUEST = BaseError(
        status=HTTPStatus.BAD_REQUEST,
        code=1202,
        message="Cannot update friend request",
    )

    CANNOT_DELETE_FRIEND_REQUEST = BaseError(
        status=HTTPStatus.BAD_REQUEST,
        code=1203,
        message="Cannot delete friend request",
    )
    
    FRIEND_REQUEST_EXISTED = BaseError(
        status=HTTPStatus.BAD_REQUEST,
        code=1204,
        message="Friend request existed",
    )

    USER_NOT_FOUND = BaseError(
        status=HTTPStatus.BAD_REQUEST,
        code=1205,
        message="User not found",
    )
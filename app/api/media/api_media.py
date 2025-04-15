import uuid
from typing import Any

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm.session import Session
from app.helpers.login_manager import login_required
from app.models import User
from app.api.media.schema_media import (
    FileDownloadResponse,
    FileUploadResponse,
    GetPublicFileUrlResponse,
    GetPublicFileUrlsResponse,
)
from app.core.config import settings
from app.db.base import get_db
from app.exception.zalo_error import ZaloError
from app.models.model_message import MessageModel
from app.schemas.sche_base import DataResponse
from app.services.aws.s3.s3 import S3Service
from app.services.aws.s3.schema import S3DocumentSchema

router = APIRouter()


@router.get("/me", response_model=DataResponse[GetPublicFileUrlsResponse])
def get_all_user_media(
    user: User = Depends(login_required),
    s3_service: S3Service = Depends(),
    db: Session = Depends(get_db),
) -> Any:
    list_media = (
        db.query(MessageModel)
        .filter(
            (MessageModel.sender_id == user.id)
            & (~MessageModel.message_type.in_(["text", "sticker"]))
        )
        .all()
    )
    return DataResponse().success_response(
        data=GetPublicFileUrlsResponse(
            urls=[
                GetPublicFileUrlResponse(
                    url=str(
                        s3_service.generate_s3_url(key=media.content, is_public=True)
                    )
                )
                for media in list_media
            ]
        )
    )


@router.post("/upload", response_model=DataResponse[FileUploadResponse])
def media_upload_file(
    user: User = Depends(login_required),
    is_public: bool = False,
    file: UploadFile = File(...),
    s3_service: S3Service = Depends(),
) -> Any:
    # Không thể để UploadFile trong BaseModel vì nó không phải là kiểu JSON.
    try:
        s3_key = s3_service.upload(file=file, user_id=user.id, is_public=is_public)
        s3_object = S3DocumentSchema(s3_key=s3_key, document_id=uuid.uuid4())
        return DataResponse().success_response(
            data=FileUploadResponse(key=s3_object.s3_key)
        )
    except Exception:
        raise ZaloError.CANNOT_UPLOAD_FILE.as_http_exception()


@router.post(
    "/download", response_model=DataResponse[FileDownloadResponse], deprecated=True
)
def media_download_file(
    s3_key: str = Form(..., min_length=1, max_length=255),
    user_id: str = Form(..., min_length=1, max_length=50),
    s3_service: S3Service = Depends(),
) -> Any:
    try:
        local_file_path = s3_service.download(
            key=s3_key, file_name=str(uuid.uuid4()), folder=settings.saved_documents
        )
        return DataResponse().success_response(
            data=FileDownloadResponse(local_file_path=local_file_path)
        )
    except Exception as e:
        raise ZaloError.CANNOT_DOWNLOAD_FILE.as_http_exception(str(e))


@router.get(
    "/get-public-file-url", response_model=DataResponse[GetPublicFileUrlResponse]
)
def media_get_public_file_url(
    s3_key: str, is_public: bool = False, s3_service: S3Service = Depends()
) -> Any:
    try:
        public_url = s3_service.generate_s3_url(key=s3_key, is_public=is_public)
        return DataResponse().success_response(
            data=GetPublicFileUrlResponse(url=str(public_url))
        )
    except Exception as e:
        raise ZaloError.CANNOT_DOWNLOAD_FILE.as_http_exception(str(e))

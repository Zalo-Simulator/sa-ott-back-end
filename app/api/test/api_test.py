import uuid
from typing import Any

from fastapi import APIRouter, Depends

from app.api.test.schema_test import (
    FileDownloadRequest,
    FileDownloadResponse,
    FileUploadRequest,
    FileUploadResponse,
    GetPublicFileUrlResponse,
    GetPublicFileUrlRequest,
)
from app.core.config import settings
from app.exception.zalo_error import ZaloError
from app.schemas.sche_base import DataResponse
from app.services.aws.s3.s3 import S3Service
from app.services.aws.s3.schema import S3DocumentSchema

router = APIRouter()


@router.post("/upload", response_model=DataResponse[FileUploadResponse])
def test_upload_file(
    payload: FileUploadRequest, s3_service: S3Service = Depends()
) -> Any:
    try:
        s3_key = s3_service.upload(file=payload.file, user_id=payload.user_id)
        s3_object = S3DocumentSchema(s3_key=s3_key, document_id=uuid.uuid4())
        return DataResponse().success_response(data=s3_object)
    except Exception:
        raise ZaloError.CANNOT_UPLOAD_FILE.as_http_exception()


@router.post(
    "/download", response_model=DataResponse[FileDownloadResponse], deprecated=True
)
def test_download_file(
    payload: FileDownloadRequest, s3_service: S3Service = Depends()
) -> Any:
    try:
        local_file_path = s3_service.download(
            key=payload.key, user_id=payload.user_id, folder=settings.saved_documents
        )
        return DataResponse().success_response(data=FileDownloadResponse())
    except Exception:
        raise ZaloError.CANNOT_DOWNLOAD_FILE.as_http_exception()


@router.get(
    "/get-public-file-url", response_model=DataResponse[GetPublicFileUrlResponse]
)
def test_get_public_file_url(
    payload: GetPublicFileUrlRequest, s3_service: S3Service = Depends()
) -> Any:
    try:
        public_url = s3_service.generate_s3_url(key=payload.key, is_public=True)
        return DataResponse().success_response(
            data=GetPublicFileUrlResponse(url=public_url)
        )
    except Exception:
        raise ZaloError.CANNOT_DOWNLOAD_FILE.as_http_exception()

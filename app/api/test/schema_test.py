from pydantic import BaseModel, Field
from fastapi import UploadFile


class FileUploadRequest(BaseModel):
    file: UploadFile
    user_id: str = Field(..., min_length=1, max_length=50)
    is_public: bool = False


class FileDownloadRequest(BaseModel):
    key: str = Field(..., min_length=1, max_length=255)
    user_id: str = Field(..., min_length=1, max_length=50)


class FileUploadResponse(BaseModel):
    status: str
    key: str


class FileDownloadResponse(BaseModel):
    key: str
    url: str = None


class GetPublicFileUrlRequest(BaseModel):
    key: str


class GetPublicFileUrlResponse(BaseModel):
    url: str

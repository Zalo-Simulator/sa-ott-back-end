from pydantic import BaseModel, Field
from typing import Union


class FileDownloadRequest(BaseModel):
    key: str = Field(..., min_length=1, max_length=255)
    user_id: str = Field(..., min_length=1, max_length=50)


class FileUploadResponse(BaseModel):
    key: str


class FileDownloadResponse(BaseModel):
    local_file_path: Union[str, None]


class GetPublicFileUrlRequest(BaseModel):
    key: str


class GetPublicFileUrlResponse(BaseModel):
    url: str

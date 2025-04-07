from uuid import UUID

from app.exception.zalo_error import ZaloError
from app.core.config import settings
from pydantic import BaseModel
import logging

logger = logging.getLogger()


class S3DocumentSchema(BaseModel):
    # https://docs.pydantic.dev/latest/concepts/validators/#field-validators
    s3_key: str  # This is a key provided by S3 after uploading
    document_id: UUID  # This is document id

    # This is original document filename
    @property
    def file_name(self) -> str:
        return self.s3_key.rstrip("/").split("/")[-1]

    # user id
    @property
    def user_id(self) -> UUID:
        try:
            return UUID(self.s3_key.rstrip("/").split("/")[1])
        except Exception as e:
            logger.warning(
                f"Can not parse user_id from S3DocumentSchema payload due to {e}"
            )
            raise ZaloError.GET_PAYLOAD_PROPERTY_FAILED.as_http_exception()

    # This is server's path to store downloaded document
    @property
    def folder(self) -> str:
        return settings.saved_documents

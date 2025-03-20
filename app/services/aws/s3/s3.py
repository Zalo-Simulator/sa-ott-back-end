import io
import os
import uuid
from typing import BinaryIO, Union

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import UploadFile

from app.exception.zalo_error import ZaloError
from app.services.aws import aws_credentials_dummy
from app.core.config import settings
from app.utils.string_utils import StringUtils
from app.helpers.logging import logger


class S3Service:
    def __init__(self, bucket: str = settings.aws.s3.private.bucket) -> None:
        self.region = settings.aws.AWS_REGION
        self.s3 = boto3.client(
            "s3",
            region_name=self.region,
            endpoint_url=settings.aws.AWS_INTERNAL_ENDPOINT_URL,
            **aws_credentials_dummy,
        )
        if bucket is None:
            # default is private
            bucket = "zalo-private-test"
        self.bucket = bucket
        self.string_helper = StringUtils()

    def _generate_key(
        self,
        user_id: uuid.UUID,
        file_name: str,
        prefix: str = "documents",
        origin_file_name: bool = True,
    ):
        if origin_file_name:
            file_name = f"{self.string_helper.generate_random_string()}/{file_name}"
        return f"{prefix}/{user_id}/{file_name}"

    def _upload_file_obj(
        self, file_obj: Union[UploadFile, BinaryIO], key: str, is_public: bool = False
    ):
        try:
            self.s3.upload_fileobj(
                Fileobj=file_obj,
                Bucket=self.bucket,
                Key=key,
                ExtraArgs={"ACL": "public-read"} if is_public is True else {},
            )
            return key
        except (BotoCoreError, ClientError) as e:
            logger.error(e)
            raise ZaloError.INTERNAL_SERVER_ERROR.as_http_exception(
                custom_message="Failed to upload s3 file"
            )

    def upload(
        self,
        file: Union[UploadFile, BinaryIO],
        user_id: uuid.UUID,
        key: Union[str, None] = None,
        prefix: str = "documents",
        origin_file_name: bool = True,
        is_public: bool = False,
    ) -> str:
        """Upload file to S3 bucket
        @file: the file to upload
        @user_id: the user id who uploads the file
        @key: the key of the file in S3 bucket
        @prefix: the prefix of the file in S3 bucket
        @origin_file_name: if True, the file name will be the same as the original file name
        @is_public: if True, the file will be public
        """
        if isinstance(file, io.BytesIO):  # Handle in-memory file
            file_obj = file
        else:
            file_obj = file.file  # Handle UploadFile-like objects
        if key is None:
            key = self._generate_key(
                user_id=user_id,
                file_name=file.filename,
                prefix=prefix,
                origin_file_name=origin_file_name,
            )
        return self._upload_file_obj(file_obj=file_obj, key=key, is_public=is_public)

    def upload_from_path(
        self,
        file_path: str,
        user_id: uuid.UUID,
        key: Union[str, None] = None,
        prefix: str = "documents",
        origin_file_name: bool = True,
        is_public: bool = False,
    ) -> str:
        """Upload file from local path to S3 bucket
        @file_path: the path of the file to upload
        @user_id: the user id who uploads the file
        @key: the key of the file in S3 bucket
        @prefix: the prefix of the file in S3 bucket
        @origin_file_name: if True, the file name will be the same as the original file name
        @is_public: if True, the file will be public
        """
        if key is None:
            key = self._generate_key(
                user_id=user_id,
                file_name=os.path.basename(file_path),
                prefix=prefix,
                origin_file_name=origin_file_name,
            )
        with open(file_path, "rb") as file:
            return self._upload_file_obj(file_obj=file, key=key, is_public=is_public)

    def upload_from_content(
        self,
        content: bytes,
        key: str,
        is_public: bool = False,
    ) -> str:
        try:
            self.s3.put_object(
                Body=content,
                Bucket=self.bucket,
                Key=key,
                ACL="public-read" if is_public else "private",
            )
            return key
        except (BotoCoreError, ClientError) as e:
            logger.error(e)
            raise ZaloError.INTERNAL_SERVER_ERROR.as_http_exception(
                custom_message="Failed to upload s3 file"
            )

    def delete(self, key: str) -> None:
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=key)
        except Exception as e:
            logger.error(e)
            raise ZaloError.INTERNAL_SERVER_ERROR.as_http_exception(
                custom_message="Failed to delete s3 file"
            )

    def move(self, old_key: str, new_key: str) -> None:
        try:
            self.s3.copy_object(
                Bucket=self.bucket,
                CopySource={"Bucket": self.bucket, "Key": old_key},
                Key=new_key,
            )
            self.s3.delete_object(Bucket=self.bucket, Key=old_key)
        except Exception as e:
            logger.error(e)
            raise ZaloError.INTERNAL_SERVER_ERROR.as_http_exception(
                custom_message="Failed to delete s3 file"
            )

    def download(self, key: str, file_name: str, folder: str) -> str:
        """Download file from S3 bucket to local
        @key: the private key of the file in S3 bucket
        @file_name: the name of the file after downloading
        @folder: the folder to save the file
        """
        try:
            file_path = os.path.join(folder, file_name)
            if not os.path.exists(file_path):
                os.makedirs(folder, exist_ok=True)
                self.s3.download_file(Bucket=self.bucket, Key=key, Filename=file_path)
                logger.info(f"S3 Downloaded {key} to {file_name}")
            return file_path
        except Exception as e:
            logger.error(e)

    def download_to_memory(self, key: str) -> bytes:
        try:
            response = self.s3.get_object(Bucket=self.bucket, Key=key)
            return response["Body"].read()
        except Exception as e:
            logger.error(e)

    def generate_s3_url(
        self, key: str, expiration: Union[int, None] = None, is_public: bool = False
    ):
        try:
            if is_public is False:
                if not expiration:
                    expiration = settings.aws.s3.private.presigned_url_expiration
                return self.s3.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self.bucket, "Key": key},
                    ExpiresIn=expiration,
                )
            else:
                if settings.environment in ["local", "test"]:
                    return (
                        f"{settings.aws.AWS_EXTERNAL_ENDPOINT_URL}/{self.bucket}/{key}"
                    )
                return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{key}"
        except ClientError as e:
            logger.error(e)
            return None

    def update_file(self, key: str, file_content):
        """
        Update an existing file in S3 bucket.
        """
        try:
            response = self.s3.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=file_content,
            )
            return response
        except Exception as e:
            logger.info(
                f"S3 cannot update the file with <{type(file_content)}> type to {key.split('.')[-1]} extension due to {e}"
            )

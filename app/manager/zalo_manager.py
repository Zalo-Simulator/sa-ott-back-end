from app.services.aws.s3.s3 import S3Service
from app.core.config import settings


class ZaloManager:
    def __init__(self):
        self.s3 = S3Service(bucket=settings.aws.s3.private.bucket)
        # TODO

from app.core.config import settings

# Localstack issue
if settings.environment in ["local", "test"]:
    # localstack dummy credentials
    aws_credentials_dummy = {
        "aws_access_key_id": "dummy",
        "aws_secret_access_key": "dummy",
    }
else:
    aws_credentials_dummy = {
        "aws_access_key_id": settings.aws.AWS_ACCESS_KEY_ID,
        "aws_secret_access_key": settings.aws.AWS_SECRET_ACCESS_KEY,
    }

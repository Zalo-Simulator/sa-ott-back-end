#!/bin/bash

REGION="us-east-1"
BUCKET_NAME_PUBLIC="zalo-public-test"
BUCKET_NAME_PRIVATE="zalo-private-test"

create_bucket_if_not_exists() {
    local bucket_name=$1
    # Check if bucket already exists
    bucket_exists=$(awslocal s3 ls | grep "$bucket_name")
    if [ -z "$bucket_exists" ]; then
        # Bucket does not exist, create it
        awslocal s3 mb s3://$bucket_name --region $REGION
        echo "Bucket $bucket_name created."
    else
        echo "Bucket $bucket_name already exists."
    fi
}

create_bucket_if_not_exists $BUCKET_NAME_PUBLIC
create_bucket_if_not_exists $BUCKET_NAME_PRIVATE

echo '
{
    "CORSRules": [
        {
            "AllowedOrigins": ["*"],
            "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
            "AllowedHeaders": ["*"]
        }
    ]
}' > cors-config.json
awslocal s3api put-bucket-cors --bucket $BUCKET_NAME_PUBLIC --cors-configuration file://cors-config.json
awslocal s3api put-bucket-cors --bucket $BUCKET_NAME_PRIVATE --cors-configuration file://cors-config.json

# Clean up CORS configuration file
rm cors-config.json
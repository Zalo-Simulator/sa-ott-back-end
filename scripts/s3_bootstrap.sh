#!/bin/bash

echo "Creating S3 buckets..."

set -euo pipefail

buckets=(
  "zalo-private-test"
  "zalo-public-test"
)

# Endpoint URL for LocalStack
endpoint_url="http://localhost:4566"

# Localstack rules
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

for bucket_name in "${buckets[@]}"; do
    awslocal --endpoint-url="$endpoint_url" s3api create-bucket --bucket "$bucket_name"
    awslocal s3api put-bucket-cors --bucket "$bucket_name" --cors-configuration file://cors-config.json
    awslocal s3api get-bucket-cors --bucket "$bucket_name"
done

# Clean up CORS configuration file
rm cors-config.json

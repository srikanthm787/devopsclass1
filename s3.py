import boto3
import json

# Initialize the S3 client
s3_client = boto3.client('s3')

def get_s3_buckets():
    """Retrieve all S3 buckets in the AWS account."""
    response = s3_client.list_buckets()
    return response['Buckets']

def get_bucket_policy(bucket_name):
    """Retrieve the bucket policy for an S3 bucket."""
    try:
        policy_response = s3_client.get_bucket_policy(Bucket=bucket_name)
        policy = policy_response['Policy']
        return json.loads(policy)
    except s3_client.exceptions.NoSuchBucketPolicy:
        return None

def get_bucket_lifecycle_configuration(bucket_name):
    """Retrieve the lifecycle configuration for an S3 bucket."""
    try:
        lifecycle_response = s3_client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
        return lifecycle_response['Rules']
    except s3_client.exceptions.NoSuchLifecycleConfiguration:
        return None

def get_bucket_tags(bucket_name):
    """Retrieve the tags for an S3 bucket."""
    try:
        tag_response = s3_client.get_bucket_tagging(Bucket=bucket_name)
        return tag_response['TagSet']
    except s3_client.exceptions.NoSuchTagSet:
        return None

def get_bucket_cors(bucket_name):
    """Retrieve the CORS configuration for an S3 bucket."""
    try:
        cors_response = s3_client.get_bucket_cors(Bucket=bucket_name)
        return cors_response['CORSRules']
    except s3_client.exceptions.NoSuchCORSConfiguration:
        return None

def get_bucket_logging(bucket_name):
    """Retrieve the logging configuration for an S3 bucket."""
    logging_response = s3_client.get_bucket_logging(Bucket=bucket_name)
    return logging_response.get('LoggingEnabled')

def get_bucket_accelerate_configuration(bucket_name):
    """Retrieve the transfer acceleration configuration for an S3 bucket."""
    accelerate_response = s3_client.get_bucket_accelerate_configuration(Bucket=bucket_name)
    return accelerate_response['Status'] if 'Status' in accelerate_response else None

def get_bucket_versioning(bucket_name):
    """Retrieve the versioning configuration for an S3 bucket."""
    versioning_response = s3_client.get_bucket_versioning(Bucket=bucket_name)
    return versioning_response.get('Status')

def get_bucket_encryption(bucket_name):
    """Retrieve the encryption configuration for an S3 bucket."""
    try:
        encryption_response = s3_client.get_bucket_encryption(Bucket=bucket_name)
        return encryption_response['ServerSideEncryptionConfiguration']
    except s3_client.exceptions.ClientError:
        return None

def get_bucket_notifications(bucket_name):
    """Retrieve the notification configuration for an S3 bucket."""
    try:
        notification_response = s3_client.get_bucket_notification_configuration(Bucket=bucket_name)
        return notification_response
    except s3_client.exceptions.ClientError:
        return None

def generate_terraform_code(bucket_name, region, policy, lifecycle_rules, tags, cors, logging, accelerate, versioning, encryption, notifications):
    """Generate Terraform code for an S3 bucket, including its full configuration."""
    policy_block = f"""
resource "aws_s3_bucket_policy" "{bucket_name}_policy" {{
  bucket = aws_s3_bucket.{bucket_name}.id
  policy = <<POLICY
{json.dumps(policy, indent=2)}
POLICY
}}
""" if policy else ""

    lifecycle_block = ""
    if lifecycle_rules:
        lifecycle_rules_json = json.dumps(lifecycle_rules, indent=2)
        lifecycle_block = f"""
resource "aws_s3_bucket_lifecycle_configuration" "{bucket_name}_lifecycle" {{
  bucket = aws_s3_bucket.{bucket_name}.id
  rule = {lifecycle_rules_json}
}}
"""

    tags_block = f"tags = {json.dumps({tag['Key']: tag['Value'] for tag in tags}, indent=2)}" if tags else ""

    cors_block = f"cors_rule = {json.dumps(cors, indent=2)}" if cors else ""

    logging_block = f"""
logging {{
  target_bucket = "{logging['TargetBucket']}"
  target_prefix = "{logging['TargetPrefix']}"
}}
""" if logging else ""

    accelerate_block = f"transfer_acceleration_status = "{accelerate}"" if accelerate else ""

    versioning_block = f"""
versioning {{
  enabled = {str(versioning == 'Enabled').lower()}
}}
""" if versioning else ""

    encryption_block = f"""
server_side_encryption_configuration = <<ENCRYPTION
{json.dumps(encryption, indent=2)}
ENCRYPTION
""" if encryption else ""

    notifications_block = ""
    if notifications:
        notifications_block = f"""
resource "aws_s3_bucket_notification" "{bucket_name}_notifications" {{
  bucket = aws_s3_bucket.{bucket_name}.id
  notification_configuration = <<NOTIFICATIONS
{json.dumps(notifications, indent=2)}
NOTIFICATIONS
}}
"""

    return f"""
resource "aws_s3_bucket" "{bucket_name}" {{
  bucket = "{bucket_name}"
  {tags_block}
  {cors_block}
  {logging_block}
  {accelerate_block}
  {versioning_block}
  {encryption_block}
}}

{policy_block}

{lifecycle_block}

{notifications_block}

output "{bucket_name}_details" {{
  value = jsonencode({{
    bucket_name = "{bucket_name}",
    region      = "{region}"
  }})
}}
""".strip()

def main():
    buckets = get_s3_buckets()
    terraform_code = []

    print("Detected S3 buckets:")
    for bucket in buckets:
        bucket_name = bucket['Name']

        # Get bucket location
        location_response = s3_client.get_bucket_location(Bucket=bucket_name)
        region = location_response['LocationConstraint'] or 'us-east-1'

        # Get bucket configurations
        policy = get_bucket_policy(bucket_name)
        lifecycle_rules = get_bucket_lifecycle_configuration(bucket_name)
        tags = get_bucket_tags(bucket_name)
        cors = get_bucket_cors(bucket_name)
        logging = get_bucket_logging(bucket_name)
        accelerate = get_bucket_accelerate_configuration(bucket_name)
        versioning = get_bucket_versioning(bucket_name)
        encryption = get_bucket_encryption(bucket_name)
        notifications = get_bucket_notifications(bucket_name)

        print(f"- {bucket_name} (Region: {region})")

        # Generate Terraform code for the bucket
        terraform_code.append(generate_terraform_code(bucket_name, region, policy, lifecycle_rules, tags, cors, logging, accelerate, versioning, encryption, notifications))

    # Write the Terraform code to a file
    with open("s3_buckets.tf", "w") as f:
        f.write("\n\n".join(terraform_code))

    print("\nTerraform code has been written to 's3_buckets.tf'.")

if __name__ == "__main__":
    main()

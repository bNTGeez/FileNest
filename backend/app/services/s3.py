import os 
from boto3 import client as boto3_client
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

S3_BUCKET = os.getenv('S3_BUCKET_NAME')
AWS_REGION = os.getenv('AWS_REGION')
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

s3 = boto3_client(
  's3',
  region_name=AWS_REGION,
  aws_access_key_id=AWS_ACCESS_KEY,
  aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

async def upload_file(file_object, key) -> str:
  """
    Uploads a file-like object under `key` in your bucket.
    Returns the file URL on success.
    """
  try:
    s3.upload_fileobj(
      Fileobj=file_object,
      Bucket=S3_BUCKET,
      Key=key,
      ExtraArgs={
        "ACL": "private"  # Only bucket owner can access directly
      }
    )
  except ClientError as e:
    raise Exception(f"Error uploading file to S3: {e}")
  
  # Generate a URL for immediate reference (won't be accessible without authentication)
  return f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{key}"

def generate_presigned_url(key: str, expiration: int = 300) -> str:
  """
    Generates a presigned URL for the file under `key` in your bucket.
    Returns the presigned URL on success.
    Default expiration is 5 minutes.
    """
  try:
    response = s3.generate_presigned_url(
      ClientMethod='get_object',
      Params={
        'Bucket': S3_BUCKET,
        'Key': key
      },
      ExpiresIn=expiration
    )
    return response
  except ClientError as e:
    raise Exception(f"Error generating presigned URL: {e}")
  
  
  
    
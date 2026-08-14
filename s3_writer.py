import boto3
import os
from dotenv import load_dotenv

# Load secret values from the .env file
load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
BUCKET_NAME = os.getenv("BUCKET_NAME")

# Create a connection to AWS S3, using our credentials
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)


def upload_to_s3(local_file_path: str, s3_key: str):
    """
    Uploads a file from your computer to the S3 bucket.

    local_file_path: where the file currently is on your laptop
    s3_key: the 'path/name' you want it saved as inside the S3 bucket
    """
    s3_client.upload_file(local_file_path, BUCKET_NAME, s3_key)
    print(f"Uploaded {local_file_path} -> s3://{BUCKET_NAME}/{s3_key}")


# This block only runs if you run this file directly (a simple test)
if __name__ == "__main__":
    # Create a tiny sample file to test the upload
    with open("test_sample.txt", "w") as f:
        f.write("This is a test file to confirm S3 upload works.")

    upload_to_s3("test_sample.txt", "raw/test/test_sample.txt")
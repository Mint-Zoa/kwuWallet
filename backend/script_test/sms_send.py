import boto3
from random import randint

client = boto3.client(
    "sns",
    aws_access_key_id="aws_access_key_id",
    aws_secret_access_key="aws_secret_access_key",
    region_name="region_name"
)

client.publish(
    PhoneNumber="PhoneNumber",
    Message="[KW] Verification code: {}\nDo not share this code anybody."
        .format(randint(100000, 999999))
)

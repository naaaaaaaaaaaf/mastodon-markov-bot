#!/usr/bin/env python3
import os
import boto3
from botocore.exceptions import ClientError


s3 = boto3.resource('s3')


def get_file(key, file_path):
    try:
        bucketName = os.environ["S3_BUCKET"]
        object_summery = s3.ObjectSummary(bucketName, key)
        s3.Bucket(bucketName).download_file(key, file_path)
        print("File downloaded: {} to {}".format(key, file_path))
        return True, object_summery.last_modified.timestamp()
    except ClientError:
        print("File not found: {}".format(key))
    return False, None


def put_file(key, file_path):
    s3.Bucket(os.environ["S3_BUCKET"]).upload_file(file_path, key)
    print("File uploaded: {} to {}".format(file_path, key))

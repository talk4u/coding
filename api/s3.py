from boto.s3.connection import S3Connection
from boto.s3.key import Key
from django.conf import settings


def read_file(key):
    s3 = S3Connection(settings.AWS_ACCESS_KEY_ID,
                      settings.AWS_SECRET_ACCESS_KEY,
                      is_secure=True)
    bucket = s3.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
    k = Key(bucket, key)
    k.open()
    return k.read()


def generate_private_url(key):
    s3 = S3Connection(settings.AWS_ACCESS_KEY_ID,
                      settings.AWS_SECRET_ACCESS_KEY,
                      is_secure=True)
    # Create a URL valid for 60 seconds.
    return s3.generate_url(60, 'GET',
                           bucket=settings.AWS_STORAGE_BUCKET_NAME,
                           key=key,
                           force_http=True)


def get_submission_path(instance, filename):
    extension = filename.split(".")[-1]
    return 'submission/{}/code.{}'.format(instance.id, extension)

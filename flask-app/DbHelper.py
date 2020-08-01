import configparser
import boto3


def singleton(cls, *args, **kw):
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return _singleton


@singleton
class DbHelper:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')

        self.tenant = config['DEFAULT']['TENANT']
        self.region = config['DEFAULT']['REGION_NAME']
        self.s3 = boto3.resource('s3',
                               aws_access_key_id=config['DEFAULT']['ACCESS_KEY'],
                               aws_secret_access_key=config['DEFAULT']['SECRET_KEY'],
                               region_name=config['DEFAULT']['REGION_NAME'])
        self.bucket_name = config['DEFAULT']['BUCKET_NAME']

    def get_s3(self):
        return self.s3

    def get_tenant(self):
        return self.tenant

    def get_bucket_name(self):
        return self.bucket_name

    def get_region(self):
        return self.region

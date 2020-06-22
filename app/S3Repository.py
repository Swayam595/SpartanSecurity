import configparser
import boto3
import botocore


class S3Repository:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')

        self.tenant = config['DEFAULT']['TENANT']
        self.region = config['DEFAULT']['REGION_NAME']
        self.s3 = boto3.resource('s3',
                                 aws_access_key_id=config['DEFAULT']['ACCESS_KEY'],
                                 aws_secret_access_key=config['DEFAULT']['SECRET_KEY'],
                                 region_name=config['DEFAULT']['REGION_NAME'])

        self.bucket_name = config['DEFAULT']['BUCKET_NAME']   # bucket name
        self.bucket = self.s3.Bucket(self.bucket_name)
        self.root = self.tenant + '/'
        self.predictions_directory = self.root + 'predictions/'  # directory path for predictions
        self.data_directory = self.root + 'data/'      # directory path for data set

        # check for if the bucket exist
        # if not create bucket
        exist = self.check_bucket(self.bucket_name)

        if exist == 0:
            try:
                self.s3.create_bucket(Bucket=self.bucket_name, CreateBucketConfiguration={
                    'LocationConstraint': self.region
                })
            except Exception:
                raise Exception("Unable to create bucket")

        elif exist == 2:
            raise Exception("Private Bucket. Forbidden Access")

        # create root directory
        self.write_file(self.root)

        # create models subdirectory
        self.write_file(self.predictions_directory)

        # create models subdirectory
        self.write_file(self.data_directory)

    def check_bucket(self, bucket_name):
        try:
            self.s3.meta.client.head_bucket(Bucket=bucket_name)
            # "Bucket Exists!
            return 1
        except botocore.exceptions.ClientError as e:
            # If a client error is thrown, then check that it was a 404 error.
            # If it was a 404 error, then the bucket does not exist.
            error_code = int(e.response['Error']['Code'])
            if error_code == 403:
                # Private Bucket. Forbidden Access!"
                return 2
            elif error_code == 404:
                # Bucket Does Not Exist!
                return 0

    def read_file(self, key):
        obj = self.s3.Object(self.bucket_name, key)
        return obj.get()['Body'].read().decode('utf-8')

    def get_file(self, key):
        obj = self.s3.Object(self.bucket_name, key)
        return obj.get()['Body']

    def write_file(self, key, body=''):
        self.bucket.put_object(Key=key, Body=body)





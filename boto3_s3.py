###############################################################################
# Communicate with Amazon SNS using Amazon's SDK library
###############################################################################
import boto3
from amazon_credentials import amazon_credentials

import argparse
import sys



###############################################################################
g_aws_access_key_id = amazon_credentials.ACCESS_KEY
g_aws_secret_access_key = amazon_credentials.SECRET_KEY
###############################################################################

###############################################################################
g_region_name = 'ap-southeast-1'
g_bucket_name = 'iotgs-iotgss3bucket-2uxeg22cmka4'
g_file_name = 'file.txt'
###############################################################################


def main(args):

    #boto3.set_stream_logger(name='botocore')

    s3 = boto3.Session(
        aws_access_key_id=g_aws_access_key_id,
        aws_secret_access_key=g_aws_secret_access_key,
        region_name=g_region_name).client('s3')

    response = s3.get_object(
        Bucket=g_bucket_name, 
        Key=g_file_name)
    file_contents = response['Body'].read().decode("utf-8")

    print(file_contents)


def parse_arguments(argv):

    parser = argparse.ArgumentParser()
    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))



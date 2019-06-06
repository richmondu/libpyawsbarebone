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
###############################################################################


def main(args):

    #boto3.set_stream_logger(name='botocore')

    sns = boto3.Session(
        aws_access_key_id=g_aws_access_key_id,
        aws_secret_access_key=g_aws_secret_access_key,
        region_name=g_region_name).client('sns')

    # Send a SMS message to the specified phone number
    response = sns.publish(PhoneNumber='+639175900612', Message='Hello World!')
    print(response)


def parse_arguments(argv):

    parser = argparse.ArgumentParser()
    parser.add_argument('--text_to_synthesize', required=False, 
        default="Hello World, how are you today?", help='Text to synthesize')
    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))



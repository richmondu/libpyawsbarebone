###############################################################################
# Communicate with Amazon Lambda using Amazon's SDK library
###############################################################################
import boto3
from amazon_credentials import amazon_credentials

import argparse
import sys
import time
import json



###############################################################################
g_aws_access_key_id = amazon_credentials.ACCESS_KEY
g_aws_secret_access_key = amazon_credentials.SECRET_KEY
###############################################################################

###############################################################################
g_region_name = 'ap-southeast-1'
###############################################################################


def main(args):

    #boto3.set_stream_logger(name='botocore')

    lambda_client = boto3.Session(
        aws_access_key_id=g_aws_access_key_id,
        aws_secret_access_key=g_aws_secret_access_key,
        region_name=g_region_name).client('lambda')

    json_data = {}
    json_data["topic"] = "arn:aws:sns:ap-southeast-1:773510983687:FT900SNStopic"
    json_data["subject"] = "This is the subject of the message."
    json_data["body"] = "This is the body of the message."
    json_data = json.dumps(json_data)
    print(json_data)

    response = lambda_client.invoke(
        FunctionName='FT900LambdaToSNS',
        Payload=json_data)
    print(response)


def parse_arguments(argv):

    parser = argparse.ArgumentParser()
    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))



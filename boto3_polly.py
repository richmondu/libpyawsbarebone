###############################################################################
# Communicate with Amazon Polly using Amazon's SDK library
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
g_region_name = 'us-east-1'
g_VoiceId = 'Joanna'
g_OutputFormat = 'pcm'
###############################################################################


def main(args):

    #boto3.set_stream_logger(name='botocore')

    text_to_synthesize = str(args.text_to_synthesize)
    #text_to_synthesize = "Hello World, how are you today?"

    response_output = "output/speech.raw"

    polly_client = boto3.Session(
        aws_access_key_id=g_aws_access_key_id,
        aws_secret_access_key=g_aws_secret_access_key,
        region_name=g_region_name).client('polly')

    response = polly_client.synthesize_speech(
        VoiceId=g_VoiceId,
        OutputFormat=g_OutputFormat, 
        Text = text_to_synthesize)

    file = open(response_output, 'wb')
    file.write(response['AudioStream'].read())
    file.close()


def parse_arguments(argv):

    parser = argparse.ArgumentParser()
    parser.add_argument('--text_to_synthesize', required=False, 
        default="Hello World, how are you today?", help='Text to synthesize')
    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))



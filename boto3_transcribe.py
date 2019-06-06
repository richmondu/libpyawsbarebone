###############################################################################
# Communicate with Amazon Polly using Amazon's SDK library
###############################################################################
import boto3
from amazon_credentials import amazon_credentials

import argparse
import sys
import time



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

    transcribe = boto3.client('transcribe')
    
    job_name = "job_name4"
    job_uri = "https://iotgs-iotgss3bucket-2uxeg22cmka4.s3-ap-southeast-1.amazonaws.com/speech.raw.wav"

    # Converting voice "Hello World, how are you today?" to text takes 0 seconds
    # Result contains a URL to a asrOutput.JSON file with security token 
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': job_uri},
        MediaFormat='wav',
        LanguageCode='en-US')

    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        print("Not ready yet...")
        time.sleep(5)
    print(status)


def parse_arguments(argv):

    parser = argparse.ArgumentParser()
    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))



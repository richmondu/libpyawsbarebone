###############################################################################
# Communicate with Amazon Pinpoint using Amazon's SDK library
###############################################################################
import boto3
from amazon_credentials import amazon_credentials
import argparse
import sys
import json



###############################################################################
g_aws_access_key_id     = amazon_credentials.ACCESS_KEY
g_aws_secret_access_key = amazon_credentials.SECRET_KEY
###############################################################################

###############################################################################
g_pinpoint_project_id = ""
g_region_name         = "us-east-1"
g_email_from          = "richmond.umagat@gmail.com"
g_sender_id           = "AmazonAWS"
g_send_text_or_email  = True
###############################################################################



###############################################################################
# https://docs.aws.amazon.com/code-samples/latest/catalog/python-pinpoint-pinpoint_send_email_message_api.py.html
###############################################################################
def send_email(pinpoint, email_recipient, email_message, email_subject):
    response = pinpoint.send_messages(
        ApplicationId=g_pinpoint_project_id,
        MessageRequest={
            'Addresses': {email_recipient: { 'ChannelType': 'EMAIL'}},
            'MessageConfiguration': {
                'EmailMessage': {
                    'FromAddress': g_email_from,
                    'SimpleEmail':  {
                        'Subject':  {'Charset': 'UTF-8', 'Data': email_subject},
                        'TextPart': {'Charset': 'UTF-8', 'Data': email_message}
                    }
                }
            }
        }
    )
    return response

###############################################################################
# https://docs.aws.amazon.com/code-samples/latest/catalog/python-pinpoint-pinpoint_send_sms_message_api.py.html
###############################################################################
def send_sms(pinpoint, sms_recipient, sms_message):
    response = pinpoint.send_messages(
        ApplicationId=g_pinpoint_project_id,
        MessageRequest={
            'Addresses': {sms_recipient: {'ChannelType': 'SMS'}},
            'MessageConfiguration': {
                'SMSMessage': {
                    'Body': sms_message
                }
            }
        }
    )
    return response


def send_message(pinpoint, recipient, message, subject=None):
    if subject is None:
        response = send_sms(pinpoint, recipient, message)
    else:
        response = send_email(pinpoint, recipient, message, subject)
    return response


def main(args):

    pinpoint = boto3.Session(
        aws_access_key_id=g_aws_access_key_id,
        aws_secret_access_key=g_aws_secret_access_key,
        region_name=g_region_name).client('pinpoint')

    subject = "Testing Amazon Pinpoint"
    message = "Hello World!"


    # sms
    recipient = "+639175900612"
    response = send_message(pinpoint, recipient, message, subject=None)
    print("Sending SMS done. {} {}".format(
        response["ResponseMetadata"]["HTTPStatusCode"]==200, 
        response["MessageResponse"]["Result"][recipient]["StatusCode"]==200))

    # email
    recipient = "richmond.umagat@yahoo.com"
    response = send_message(pinpoint, recipient, message, subject=subject)
    print("Sending EMAIL done. {} {}".format(
        response["ResponseMetadata"]["HTTPStatusCode"]==200, 
        response["MessageResponse"]["Result"][recipient]["StatusCode"]==200))

    return


def parse_arguments(argv):

    parser = argparse.ArgumentParser()
    parser.add_argument('--text_to_synthesize', required=False, 
        default="Hello World, how are you today?", help='Text to synthesize')
    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))



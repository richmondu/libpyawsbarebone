###############################################################################
# Communicate with Amazon Pinpoint using Amazon's SDK library
###############################################################################
import boto3
from amazon_credentials import amazon_credentials
import argparse
import sys



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
def send_email(pinpoint, email_recipient, email_subject, email_message):
    response = pinpoint.send_messages(
        ApplicationId=g_pinpoint_project_id,
        MessageRequest={
            'Addresses': {email_recipient: { 'ChannelType': 'EMAIL'}},
            'MessageConfiguration': {
                'EmailMessage': {
                    'FromAddress': g_email_from,
                    'SimpleEmail':  {
                        'Subject':  {'Charset': 'UTF-8', 'Data': email_subject},
                        'HtmlPart': {'Charset': 'UTF-8', 'Data': email_message}
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

def main(args):

    #boto3.set_stream_logger(name='botocore')

    pinpoint = boto3.Session(
        aws_access_key_id=g_aws_access_key_id,
        aws_secret_access_key=g_aws_secret_access_key,
        region_name=g_region_name).client('pinpoint')

    ###############################################################################
    # sms
    ###############################################################################
    if g_send_text_or_email:
        sms_recipient = "+639175900612"
        sms_message = "Hello World!"
        response = send_sms(pinpoint, sms_recipient, sms_message)
    ###############################################################################
    # email
    ###############################################################################
    else:
        email_recipient = "richmond.umagat@yahoo.com"
        email_subject   = "Pinpoint message from Richmond"
        email_message = """<html>
        <head></head>
        <body>
          <h1>Amazon Pinpoint Test (SDK for Python)</h1>
          <p>This email was sent with
            <a href='https:#aws.amazon.com/pinpoint/'>Amazon Pinpoint</a> using the
            <a href='https:#aws.amazon.com/sdk-for-python/'>
              AWS SDK for Python (Boto 3)</a>.</p>
        </body>
        </html>
                    """
        response = send_email(pinpoint, email_recipient, email_subject, email_message)

    print(response)


def parse_arguments(argv):

    parser = argparse.ArgumentParser()
    parser.add_argument('--text_to_synthesize', required=False, 
        default="Hello World, how are you today?", help='Text to synthesize')
    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))



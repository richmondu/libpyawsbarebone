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
g_pinpoint_project_id = ""                                          # UPDATE ME
g_region_name         = "us-east-1"                                 # UPDATE ME
g_email_from          = "richmond.umagat@gmail.com"                 # UPDATE ME
###############################################################################

###############################################################################
g_push_notification_service_android = "GCM"
g_push_notification_service_apple   = "APNS"
g_push_notification_service_use     = g_push_notification_service_apple
g_push_notification_token_android   = ""                            # UPDATE ME
g_push_notification_token_apple     = ""                            # UPDATE ME
###############################################################################

###############################################################################
g_send_sms = False
g_send_email = False
g_send_push_notification = True
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

###############################################################################
# https://docs.aws.amazon.com/pinpoint/latest/developerguide/send-messages-push.html
###############################################################################
def send_push_notification(pinpoint, recipient, message, title):
    print("send_push_notification")
    action = "URL"
    url = "https://www.example.com"
    priority = "normal"
    ttl = 30
    silent = False
    token = recipient["token"]
    service = recipient["service"]

    if service == g_push_notification_service_android:
        response = pinpoint.send_messages(
            ApplicationId=g_pinpoint_project_id,
            MessageRequest={
                'Addresses': {token: {'ChannelType': service}},
                'MessageConfiguration': {
                    'GCMMessage': {
                        'Action': action,
                        'Body': message,
                        'Priority' : priority,
                        'SilentPush': silent,
                        'Title': title,
                        'TimeToLive': ttl,
                        'Url': url
                    }
                }
            }
        )
    elif service == g_push_notification_service_apple:
        response = pinpoint.send_messages(
            ApplicationId=g_pinpoint_project_id,
            MessageRequest={
                'Addresses': {token: {'ChannelType': service}},
                'MessageConfiguration': {
                    'APNSMessage': {
                        'Action': action,
                        'Body': message,
                        'Priority' : priority,
                        'SilentPush': silent,
                        'Title': title,
                        'TimeToLive': ttl,
                        'Url': url
                    }
                }
            }
        )
    return response


def send_message(pinpoint, type, recipient, message, subject=None):
    if type == "sms":
        response = send_sms(pinpoint, recipient, message)
    elif type == "email":
        response = send_email(pinpoint, recipient, message, subject)
    elif type == "push_notification":
        response = send_push_notification(pinpoint, recipient, message, subject)

    return response


def main(args):

    #boto3.set_stream_logger(name='botocore')

    pinpoint = boto3.Session(
        aws_access_key_id=g_aws_access_key_id,
        aws_secret_access_key=g_aws_secret_access_key,
        region_name=g_region_name).client('pinpoint')

    subject = "Testing Amazon Pinpoint"
    message = "Hello World!"


    # sms
    if g_send_sms:
        recipient = "+639175900612"
        response = send_message(pinpoint, "sms", recipient, message, None)
        print("Sending SMS done. {} {}".format(
            response["ResponseMetadata"]["HTTPStatusCode"]==200, 
            response["MessageResponse"]["Result"][recipient]["StatusCode"]==200))

    # email
    if g_send_email:
        recipient = "richmond.umagat@yahoo.com"
        response = send_message(pinpoint, "email", recipient, message, subject)
        print("Sending EMAIL done. {} {}".format(
            response["ResponseMetadata"]["HTTPStatusCode"]==200, 
            response["MessageResponse"]["Result"][recipient]["StatusCode"]==200))

    # push notification
    if g_send_push_notification:
        if g_push_notification_service_use == g_push_notification_service_android:
            # android
            recipient = {
                "token"  : g_push_notification_token_android,
                "service": g_push_notification_service_android
            }
            print("android")
        elif g_push_notification_service_use == g_push_notification_service_apple:
            # apple
            recipient = {
                "token"  : g_push_notification_token_apple,
                "service": g_push_notification_service_apple
            }
            print("apple")

        response = send_message(pinpoint, "push_notification", recipient, message, subject)
        print(response)
        #print()
        #print("Sending PUSH NOTIFICATION done. {}".format(
        #    response['MessageResponse']['Result'][recipient]['DeliveryStatus'] == "SUCCESSFUL"))

    return


def parse_arguments(argv):

    parser = argparse.ArgumentParser()
    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))



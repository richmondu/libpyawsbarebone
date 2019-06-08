# libpyawsbarebone 


libpyawsbarebone is a bare bone Python implementation of Amazon services connectivity.
It uses plain sockets and encryption to send HTTP POST packet signed with SigV4 and sent over secure TLS tunnel.

It is useful for people who want to know how to implement Amazon connectivity from scratch
without using Amazon SDKs, such as the Python Boto3 library.

Supported Amazon Services:

    1. AWS Polly [converting text to speech]
    2. AWS SNS [sending sms/text and email]
    3. AWS Lambda [invoking serverless function]
    4. AWS IoT Core [publishing sensor data]

Instructions:

    1. Copy your Amazon security credentials (access key id and secret access key)
       https://console.aws.amazon.com/iam/home?#/security_credentials
    2. Create amazon_credentials.py
       class amazon_credentials:
           ACCESS_KEY = 'EXAMPLEACCESSKEY'
           SECRET_KEY = 'EXAMPLESECRETKEY'
    3. Update and run barebones_xxx.bat

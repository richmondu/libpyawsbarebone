###############################################################################
# Communicate with Amazon IoT using Amazon's SDK library
###############################################################################
import boto3
from amazon_credentials import amazon_credentials

import argparse
import sys
import json
import time
import random



###############################################################################
g_aws_access_key_id = amazon_credentials.ACCESS_KEY
g_aws_secret_access_key = amazon_credentials.SECRET_KEY
###############################################################################

###############################################################################
g_region_name = 'us-east-1'
###############################################################################


def main(args):

    boto3.set_stream_logger(name='botocore')

    dynamodb = boto3.Session(
        aws_access_key_id=g_aws_access_key_id,
        aws_secret_access_key=g_aws_secret_access_key,
        region_name=g_region_name).resource('dynamodb')

    table = dynamodb.Table('GreengrassDashboard-IoTGSDynamoDeviceStatusTable-1JGCAR33OAYSP')

    devices = {"hopper", "knuth", "turing"}
    while True:
        for device in devices:
            json_data = {}
            json_data["deviceId"] = device
            json_data["sensorReading"] = random.randrange(30, 41, 1)
            json_data["batteryCharge"] = random.randrange(-10, 21, 1)
            json_data["batteryDischargeRate"] = random.randrange(0, 6, 1)
            #json_data = json.dumps(json_data)
            print(json_data)

            table.put_item(Item=json_data)
            break
        break
        time.sleep(1)



def parse_arguments(argv):

    parser = argparse.ArgumentParser()
    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))



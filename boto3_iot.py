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

    #boto3.set_stream_logger(name='botocore')

    iot = boto3.Session(
        aws_access_key_id=g_aws_access_key_id,
        aws_secret_access_key=g_aws_secret_access_key,
        region_name=g_region_name).client('iot-data')

    devices = {"knuth", "turing", "hopper"}
    while True:
        for device in devices:
            json_data = {}
            json_data["deviceId"] = device
            json_data["sensorReading"] = random.randrange(30, 41, 1)
            json_data["batteryCharge"] = random.randrange(-10, 21, 1)
            json_data["batteryDischargeRate"] = random.randrange(0, 6, 1)
            json_data = json.dumps(json_data)
            print(json_data)

            topic = "device/{}/devicePayload".format(device)
            response = iot.publish(
                topic = topic,
                payload = json_data.encode())
            break
        break
        time.sleep(1)



def parse_arguments(argv):

    parser = argparse.ArgumentParser()
    parser.add_argument('--text_to_synthesize', required=False, 
        default="Hello World, how are you today?", help='Text to synthesize')
    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))



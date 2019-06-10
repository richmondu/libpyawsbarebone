###############################################################################
# Communicate with Amazon Lambda using plain sockets and encryption library
###############################################################################
import socket, ssl
import hashlib, hmac
import datetime
from amazon_credentials import amazon_credentials

import argparse
import sys
import urllib.parse
import json



###############################################################################
CONFIG_AWS_ACCESS_KEY     = amazon_credentials.ACCESS_KEY
CONFIG_AWS_SECRET_KEY     = amazon_credentials.SECRET_KEY
###############################################################################

###############################################################################
CONFIG_AWS_SERVICE        = 's3'
CONFIG_AWS_REGION         = 'ap-southeast-1'

CONFIG_HTTP_METHOD        = 'GET'
CONFIG_HTTP_API           = '/file.txt'
CONFIG_HTTP_CONTENT_TYPE  = 'application/json'
CONFIG_AWS_S3_BUCKET_NAME = 'iotgs-iotgss3bucket-2uxeg22cmka4'

CONFIG_AWS_HEADERS        = 'host;x-amz-content-sha256;x-amz-date'
CONFIG_AWS_ALGORITHM      = 'AWS4-HMAC-SHA256'
CONFIG_AWS_SIG4_REQUEST   = 'aws4_request'

CONFIG_AWS_HOST           = CONFIG_AWS_SERVICE + '.' + CONFIG_AWS_REGION + '.amazonaws.com'
CONFIG_AWS_PORT           = 443
CONFIG_AWS_ENDPOINT       = 'https://' + CONFIG_AWS_HOST + CONFIG_HTTP_API

CONFIG_MAX_RECV_SIZE      = 512
###############################################################################


class s3_barebones:
    def __init__(self):
        self.session = None

    def sign(self, key, msg):
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

    def getSignatureKey(self, key, dateStamp, regionName, serviceName):
        kDate = self.sign(('AWS4' + key).encode('utf-8'), dateStamp)
        print("kDate=[{}] {}".format(dateStamp, kDate))
        kRegion = self.sign(kDate, regionName)
        print("kRegion=[{}] {}".format(regionName, kRegion))
        kService = self.sign(kRegion, serviceName)
        print("kService=[{}] {}".format(serviceName, kService))
        kSigning = self.sign(kService, CONFIG_AWS_SIG4_REQUEST)
        print("kSigning=[{}] {}".format(CONFIG_AWS_SIG4_REQUEST, kSigning))
        return kSigning

    def generateCanonicalRequest(self, amz_date, request_parameters):
        payload_hash = hashlib.sha256(request_parameters.encode("utf-8")).hexdigest()
        print("payload_hash={}".format(payload_hash))

        #canonical_headers  = 'content-type:' + CONFIG_HTTP_CONTENT_TYPE + '\n'
        canonical_headers = 'host:' + CONFIG_AWS_S3_BUCKET_NAME + '.' + CONFIG_AWS_HOST + '\n'
        canonical_headers += 'x-amz-content-sha256:' + payload_hash + '\n'
        canonical_headers += 'x-amz-date:' + amz_date + '\n'
        print("canonical_headers={}".format(canonical_headers))
        
        canonical_request  = CONFIG_HTTP_METHOD + '\n'
        canonical_request += CONFIG_HTTP_API + '\n'
        canonical_request += '' + '\n'
        canonical_request += canonical_headers + '\n'
        canonical_request += CONFIG_AWS_HEADERS + '\n'
        canonical_request += payload_hash
        return canonical_request

    def generateStringToSign(self, date_stamp, amz_date, credential_scope, canonical_request):
        canonical_request_hash = hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
        print("canonical_request_hash={}".format(canonical_request_hash))
        
        string_to_sign = CONFIG_AWS_ALGORITHM + '\n'
        string_to_sign += amz_date + '\n'
        string_to_sign += credential_scope + '\n'
        string_to_sign += canonical_request_hash
        return string_to_sign

    def calculateSignature(self, date_stamp, string_to_sign):
        signing_key = self.getSignatureKey(CONFIG_AWS_SECRET_KEY, date_stamp, CONFIG_AWS_REGION, CONFIG_AWS_SERVICE)
        signature = hmac.new(signing_key, (string_to_sign).encode('utf-8'), hashlib.sha256).hexdigest()
        return signature

    def generateAuthorizationHeader(self, amz_date, credential_scope, signature):
        authorization_header = CONFIG_AWS_ALGORITHM # + ' '
        #authorization_header += 'Credential=' + CONFIG_AWS_ACCESS_KEY + '/' + credential_scope + ', '
        #authorization_header += 'SignedHeaders=' + CONFIG_AWS_HEADERS + ', '
        #authorization_header += 'Signature=' + signature
        headers = {
            #'Content-Type':CONFIG_HTTP_CONTENT_TYPE,
            'X-Amz-Content-SHA256': signature,
            'X-Amz-Date':amz_date,
            'Authorization':authorization_header }
        return headers

    def getDateTimeStamps(self):
        t = datetime.datetime.utcnow()
        amz_date = t.strftime('%Y%m%dT%H%M%SZ')
        date_stamp = t.strftime('%Y%m%d') # Date w/o time, used in credential scope
        #amz_date = '20190610T070444Z'
        #date_stamp = '20190610'
        print("amz_date:\r\n{}\r\n".format(amz_date))
        print("date_stamp:\r\n{}\r\n".format(date_stamp))
        return (amz_date, date_stamp)

    def generatePacket(self, amz_date, credential_scope, signature, request_parameters):
        data = CONFIG_HTTP_METHOD + " " + CONFIG_HTTP_API+ " HTTP/1.1\r\n"
        data += "Host:" + CONFIG_AWS_S3_BUCKET_NAME + '.' + CONFIG_AWS_HOST +  "\r\n"
        #data += "Connection: keep-alive\r\n"
        #data += "Content-Type:"   + CONFIG_HTTP_CONTENT_TYPE + "\r\n"
        data += "X-Amz-Date:"     + amz_date + "\r\n"
        data += "X-Amz-Content-SHA256:" + hashlib.sha256(request_parameters.encode("utf-8")).hexdigest() + "\r\n"
        data += "Authorization:"  + CONFIG_AWS_ALGORITHM + " "
        data += 'Credential='     + CONFIG_AWS_ACCESS_KEY + '/' + credential_scope + ','
        data += 'SignedHeaders='  + CONFIG_AWS_HEADERS + ','
        data += 'Signature='      + signature + "\r\n"
        #data += "Content-Length:" + str(len(request_parameters)) + "\r\n"
        data += "\r\n"
        
        data += request_parameters + '\r\n'
        return data


    def connect(self):
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        self.session = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.session = context.wrap_socket(self.session, server_hostname=CONFIG_AWS_HOST)
        
        server = socket.getaddrinfo(CONFIG_AWS_HOST, CONFIG_AWS_PORT)[0][-1]
        try:
            self.session.connect(server)
        except:
            print("Error: could not connect to server. Please check if server is running!")
            self.session.close()
            self.session = None

    def sendRequest(self, request):
        self.session.sendall(request.encode("utf-8"))
        print("{} [{}]".format(request, len(request)))

    def generateRequestS3(self, message_to_send):
        return message_to_send

    def createRequestS3(self, message_to_send):

        (amz_date, date_stamp) = self.getDateTimeStamps()

        credential_scope = date_stamp + '/' + CONFIG_AWS_REGION + '/' + CONFIG_AWS_SERVICE + '/' + CONFIG_AWS_SIG4_REQUEST
        print("credential_scope:\r\n{}\r\n".format(credential_scope))

        request_parameters = self.generateRequestS3(message_to_send)
        print("request_parameters:\r\n{}\r\n".format(request_parameters))

        canonical_request = self.generateCanonicalRequest(amz_date, request_parameters)
        print("canonical_request:\r\n{}\r\n".format(canonical_request))

        string_to_sign = self.generateStringToSign(date_stamp, amz_date, credential_scope, canonical_request)
        print("string_to_sign:\r\n{}\r\n".format(string_to_sign))

        signature = self.calculateSignature(date_stamp, string_to_sign)
        print("signature:\r\n{}\r\n".format(signature))
        authorization_headers = self.generateAuthorizationHeader(amz_date, credential_scope, signature)
        print("authorization_headers:\r\n{}\r\n".format(authorization_headers))

        request_packet = self.generatePacket(amz_date, credential_scope, signature, request_parameters)
        print("request packet:\r\n{}\r\n".format(request_packet))
        return request_packet

    def recvResponseS3(self):
        self.session.settimeout(1)
        while True:
            try:
                response = self.session.recv(1024)
                if len(response) == 0:
                    break
                print("{} [{}]".format(response, len(response)))
            except:
                pass

    def close(self):
        self.session.close()


def main(args):

    client = s3_barebones()
    request_input = client.createRequestS3("")
    client.connect()
    client.sendRequest(request_input)
    client.recvResponseS3()
    client.close()


def parse_arguments(argv):

    parser = argparse.ArgumentParser()
    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))

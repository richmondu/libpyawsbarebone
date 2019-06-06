###############################################################################
# Communicate with Amazon Polly using plain sockets and encryption library
###############################################################################
import socket, ssl
import hashlib, hmac
import datetime
from amazon_credentials import amazon_credentials

import argparse
import sys



###############################################################################
CONFIG_AWS_ACCESS_KEY     = amazon_credentials.ACCESS_KEY
CONFIG_AWS_SECRET_KEY     = amazon_credentials.SECRET_KEY
###############################################################################

###############################################################################
CONFIG_AWS_SERVICE        = 'polly'
CONFIG_AWS_REGION         = 'us-east-1'

CONFIG_HTTP_METHOD        = 'POST'
CONFIG_HTTP_API           = '/v1/speech'
CONFIG_HTTP_CONTENT_TYPE  = 'application/json'

CONFIG_AWS_POLLY_VOICE_ID = "Joanna"
CONFIG_AWS_POLLY_FORMAT   = "pcm"

CONFIG_AWS_HEADERS        = 'content-type;host;x-amz-date'
CONFIG_AWS_ALGORITHM      = 'AWS4-HMAC-SHA256'
CONFIG_AWS_SIG4_REQUEST   = 'aws4_request'

CONFIG_AWS_HOST           = CONFIG_AWS_SERVICE + '.' + CONFIG_AWS_REGION + '.amazonaws.com'
CONFIG_AWS_PORT           = 443
CONFIG_AWS_ENDPOINT       = 'https://' + CONFIG_AWS_HOST + CONFIG_HTTP_API

CONFIG_MAX_RECV_SIZE      = 512
###############################################################################


class polly_barebones:
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
        canonical_headers  = 'content-type:' + CONFIG_HTTP_CONTENT_TYPE + '\n'
        canonical_headers += 'host:' + CONFIG_AWS_HOST + '\n'
        canonical_headers += 'x-amz-date:' + amz_date + '\n'
        print("canonical_headers={}".format(canonical_headers))
        
        payload_hash = hashlib.sha256(request_parameters.encode("utf-8")).hexdigest()
        print("payload_hash={}".format(payload_hash))
        
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
        authorization_header = CONFIG_AWS_ALGORITHM + ' '
        authorization_header += 'Credential=' + CONFIG_AWS_ACCESS_KEY + '/' + credential_scope + ', '
        authorization_header += 'SignedHeaders=' + CONFIG_AWS_HEADERS + ', '
        authorization_header += 'Signature=' + signature
        headers = {
            'Content-Type':CONFIG_HTTP_CONTENT_TYPE,
            'X-Amz-Date':amz_date,
            'Authorization':authorization_header }
        return headers

    def getDateTimeStamps(self):
        t = datetime.datetime.utcnow()
        amz_date = t.strftime('%Y%m%dT%H%M%SZ')
        date_stamp = t.strftime('%Y%m%d') # Date w/o time, used in credential scope
        print("amz_date:\r\n{}\r\n".format(amz_date))
        print("date_stamp:\r\n{}\r\n".format(date_stamp))    
        return (amz_date, date_stamp)

    def generatePacket(self, amz_date, credential_scope, signature, request_parameters):
        data = CONFIG_HTTP_METHOD + " " + CONFIG_HTTP_API+ " HTTP/1.1\r\n"
        data += "Host:" + CONFIG_AWS_HOST +  "\r\n"
        #data += "Connection: keep-alive\r\n"
        data += "Content-Type:"   + CONFIG_HTTP_CONTENT_TYPE + "\r\n"
        data += "X-Amz-Date:"     + amz_date + "\r\n"
        data += "Authorization:"  + CONFIG_AWS_ALGORITHM + ' '
        data += 'Credential='     + CONFIG_AWS_ACCESS_KEY + '/' + credential_scope + ','
        data += 'SignedHeaders='  + CONFIG_AWS_HEADERS + ','
        data += 'Signature='      + signature + "\r\n"
        data += "Content-Length:" + str(len(request_parameters)) + "\r\n"
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

    def generateRequestPolly(self, text):
        request = '{'
        request +=  '"OutputFormat":"' + CONFIG_AWS_POLLY_FORMAT + '",'
        request +=  '"VoiceId":"' + CONFIG_AWS_POLLY_VOICE_ID + '",'
        request +=  '"Text":"' + text + '"'
        request +=  '}'
        return request

    def createRequestPolly(self, text_to_synthesize):

        (amz_date, date_stamp) = self.getDateTimeStamps()

        credential_scope = date_stamp + '/' + CONFIG_AWS_REGION + '/' + CONFIG_AWS_SERVICE + '/' + CONFIG_AWS_SIG4_REQUEST
        print("credential_scope:\r\n{}\r\n".format(credential_scope))

        request_parameters = self.generateRequestPolly(text_to_synthesize)
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

    def recvResponsePolly(self, output_audiofile):
        self.session.settimeout(1)
        # receive response from server
        if CONFIG_AWS_POLLY_FORMAT == "pcm":
            f = open(output_audiofile,'wb')
        else:
            f = open(output_audiofile + '.'+CONFIG_AWS_POLLY_FORMAT,'wb')

        read_size = CONFIG_MAX_RECV_SIZE
        response = self.session.recv(read_size)
        index = response.find(b'\r\n\r\n')
        index += 4
        if index < len(response):
            header = response[0:index]
            response = response[index:]
        else:
            header = response[0:index]
            response = self.session.recv(read_size)

        index2 = response.find(b'\r\n')
        if index2>0 and index2<=4:
            size = response[0:index2]
            print(size)
            size = int(size.decode("utf-8"), 16) + 2
            response = response[index2+2:]
            f.write(response)
            processed = len(response)
            read_size = size - processed
            if read_size > CONFIG_MAX_RECV_SIZE:
                read_size = CONFIG_MAX_RECV_SIZE
        
        while True:
            try:
                response = self.session.recv(read_size)
                processed += len(response)
                if size == processed:
                    f.write(response[:-2])
                    processed = 0
                elif size < processed:
                    print("unexpected!!!!!!!!!!!!!!!!!!")
                    break
                else:
                    f.write(response)
                    read_size = size - processed
                    if read_size > CONFIG_MAX_RECV_SIZE:
                        read_size = CONFIG_MAX_RECV_SIZE
                    continue
            except:
                print("exception!!!!!!!!!!!!!!!!!!")
                break

            chars = b''
            while True:
                char = self.session.recv(1)
                if char == b'\r':
                    print(chars)
                    char = self.session.recv(1)
                    size = int(chars.decode("utf-8"), 16) + 2
                    read_size = size
                    if read_size > CONFIG_MAX_RECV_SIZE:
                        read_size = CONFIG_MAX_RECV_SIZE
                    break
                else:
                    chars += char
            if size == 2:
                char = self.session.recv(2)
                break
                
            #break
        f.close()

    def close(self):
        self.session.close()


def main(args):

    #text_to_synthesize = str(args.text_to_synthesize)
    text_to_synthesize = "Hello World, how are you today?"

    response_output = "output/speech_barebones.raw"

    polly = polly_barebones()
    request_input = polly.createRequestPolly(text_to_synthesize)
    polly.connect()
    polly.sendRequest(request_input)
    polly.recvResponsePolly(response_output)
    polly.close()


def parse_arguments(argv):

    parser = argparse.ArgumentParser()
    parser.add_argument('--text_to_synthesize', required=False, 
        default="Hello World, how are you today?", help='Text to synthesize')
    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))

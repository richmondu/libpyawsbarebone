# libpyawsbarebone 


libpyawsbarebone is a bare bone Python implementation of Amazon services connectivity.
It uses plain sockets and encryption to send HTTP POST packet signed with SigV4 and sent over secure TLS tunnel.

It is useful for people who want to know how to implement Amazon connectivity from scratch
without using Amazon SDKs, such as the Python Boto3 library.

Instructions:

    1. Set ACCESS_KEY and SECRET_KEY on amazon_credentials.py
    2. Update and run barebones_xxx.bat

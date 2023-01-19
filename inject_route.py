import requests
import argparse
import time
import uuid
import hmac
import hashlib
import base64
import json
import sys

## Parse args
parser = argparse.ArgumentParser(description='Scripts args')
parser.add_argument('--base-url', dest='BASE_URL', type=str, help='URL of Pritunl server without https://')
parser.add_argument('--api-token', dest='API_TOKEN', type=str, help='API_TOKEN')
parser.add_argument('--api-secret', dest='API_SECRET', type=str, help='API_SECRET')
parser.add_argument('--server-id', dest='SERVER_ID', type=str, help='SERVER_ID')
parser.add_argument('--new-route', dest='ROUTE', type=str, help='New route to add')

args = parser.parse_args()

BASE_URL = args.BASE_URL
API_TOKEN = args.API_TOKEN
API_SECRET = args.API_SECRET
SERVER_ID = args.SERVER_ID
ROUTE = args.ROUTE

def auth_request(method, path, headers=None, data=None):
    auth_timestamp = str(int(time.time()))
    auth_nonce = uuid.uuid4().hex
    auth_string = '&'.join([API_TOKEN, auth_timestamp, auth_nonce,
        method.upper(), path])
    if sys.version_info[0] < 3:
        auth_signature = base64.b64encode(hmac.new(
            API_SECRET, auth_string, hashlib.sha256).digest())
    else:
        auth_signature = base64.b64encode(hmac.new(
            API_SECRET.encode('utf-8'), auth_string.encode('utf-8'), hashlib.sha256).digest())
    auth_headers = {
        'Auth-Token': API_TOKEN,
        'Auth-Timestamp': auth_timestamp,
        'Auth-Nonce': auth_nonce,
        'Auth-Signature': auth_signature,
    }
    if headers:
        auth_headers.update(headers)
    return getattr(requests, method.lower())(
        BASE_URL + path,
        headers=auth_headers,
        data=data,
    )

## Stopping
response = auth_request(
    'PUT',
    '/server/%s/operation/stop' % SERVER_ID,
)
print(response)
assert(response.status_code == 200)


## Injecting route
routes = []

routes.append({
    'network': ROUTE,
    'nat': True,
})

response = auth_request(
    'POST',
    '/server/%s/routes' % SERVER_ID,
    headers={
        'Content-Type': 'application/json',
    },
    data=json.dumps(routes),
)
print(response)
assert(response.status_code == 200)

## Restarting
response = auth_request(
    'PUT',
    '/server/%s/operation/start' % SERVER_ID,
)
print(response)
assert(response.status_code == 200)
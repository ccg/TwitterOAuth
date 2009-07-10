#!/usr/bin/env python

# TODO unittest or doctest
# TODO abstraction for API URLs or just type out the whole thing each time?
# TODO docstrings
# TODO test with desktopRW app

import urllib
import urllib2
import webbrowser
import oauth.oauth as oauth
from datetime import datetime
from localsettings import CONSUMER_KEY, CONSUMER_SECRET

class TwitterClient(oauth.OAuthClient):
    request_token_url = 'http://twitter.com/oauth/request_token'
    access_token_url  = 'http://twitter.com/oauth/access_token'
    authorization_url = 'http://twitter.com/oauth/authorize'

    def __init__(self,
                 consumer=None, # oauth.OAuthConsumer object
                ):
        self.consumer = consumer

        # twitter only supports HMAC SHA1
        self.sig_method = oauth.OAuthSignatureMethod_HMAC_SHA1()

    def build_signed_request(self, url=None, token=None, parameters={}):
        if parameters:
            http_method = 'POST'
        else:
            http_method = 'GET'
        request = oauth.OAuthRequest.from_consumer_and_token(self.consumer,
                                                             token,
                                                             http_method,
                                                             url,
                                                             parameters)
        request.sign_request(signature_method=self.sig_method,
                             consumer=self.consumer,
                             token=token)
        return request

    def fetch_response(self, url, token=None, parameters={}):
        oauth_request = self.build_signed_request(url, token, parameters)
        data = urllib.urlencode(parameters) or None
        # FIXME is realm really needed?
        headers = oauth_request.to_header(realm='Twitter API')
        http_request = urllib2.Request(url, data, headers)
        f = urllib2.urlopen(http_request)
        response = f.read()
        f.close()
        return response

    def fetch_request_token(self):
        msg = self.fetch_response(self.request_token_url)
        request_token = oauth.OAuthToken.from_string(msg)
        return request_token

    def get_auth_url(self, token=None):
        oauth_request = self.build_signed_request(url=self.authorization_url,
                                                  token=token)
        return oauth_request.to_url()

    def fetch_access_token(self, request_token):
        response = self.fetch_response(url=self.access_token_url,
                                       token=request_token)
        access_token = oauth.OAuthToken.from_string(response)
        return access_token

    def verify_credentials(self, access_token):
        response = self.fetch_response(url="http://twitter.com/account/verify_credentials.json", token=access_token)
        return response

    def status_update(self, access_token, tweet):
        response = self.fetch_response(url='http://twitter.com/statuses/update.json',
                                       token=access_token,
                                       parameters={'status': tweet})
        return response

# screw it. global variables. yay!
consumer = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)
client = TwitterClient(consumer=consumer)
# fill in the values here to test a saved token
existing_access_token = oauth.OAuthToken.from_string('oauth_token_secret=...&oauth_token=...')

def test_new_user():
    # get an unauthed request token
    request_token = client.fetch_request_token()
    # have user authorized the app
    auth_url = client.get_auth_url(request_token)
    print auth_url
    webbrowser.open_new(auth_url)
    raw_input("press Enter after authenticating in browser... ")
    # exchange request token for access token
    access_token = client.fetch_access_token(request_token)
    print "access_token = '%s'" % access_token
    # test it
    print client.verify_credentials(access_token)

def test_existing_user():
    print client.verify_credentials(existing_access_token)

def test_POST():
    tweet = 'TEST ' + str(datetime.now())
    print client.status_update(existing_access_token, tweet)

if __name__ == '__main__':
    test_new_user()
    test_existing_user()
    test_POST()

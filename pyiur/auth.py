# -*- coding: utf-8 -*-
"""


"""

import cookielib

import requests

from pyiur.exceptions import InvalidCredentialsError

class Anonymous(object):
    """


    """

    def update(self, params = None, headers = None, cookies = None):
        return {'params': params, 'headers': headers, 'cookies': cookies,
                'auth': None}


class Cookie(object):
    """


    """

    COOKIE_REQUEST_URL = 'http://api.imgur.com/2/signin'

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def update(self, params = None, headers = None, cookies = None):
        cookies = cookies or cookielib.CookieJar()
        response = requests.post(self.COOKIE_REQUEST_URL,
                                 {'username': self.username,
                                  'password': self.password},
                                 cookies = cookies)

        if response.status_code in (400, 403):
            raise InvalidCredentialsError(
                'Error retrieving authentication cookie with the supplied '
                'username and password.')

        return {'params': params, 'headers': headers, 'cookies': cookies,
                'auth': None}


class DeveloperKey(object):
    """


    """

    def __init__(self, key):
        self.key = key

    def update(self, params = None, headers = None, cookies = None):
        params = params or {}
        params['key'] = self.key
        return {'params': params, 'headers': headers, 'cookies': cookies,
                'auth': None}

class OAuth1(object):
    """


    """

    REQUEST_TOKEN_URL = 'https://api.imgur.com/oauth/request_token'
    AUTHORIZE_URL = 'https://api.imgur.com/oauth/authorize'
    ACCESS_TOKEN_URL = 'https://api.imgur.com/oauth/access_token'

    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    def update(self, params = None, headers = None, cookies = None):
        # TODO
        return {'params': params, 'headers': headers, 'cookies': cookies,
                'auth': None}



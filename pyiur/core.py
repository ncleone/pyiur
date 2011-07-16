# -*- coding: utf-8 -*-
"""


"""

import datetime
import functools

import requests

from pyiur.auth import Anonymous as AnonAuth
from pyiur.auth import Cookie as CookieAuth
from pyiur.auth import DeveloperKey as DevAuth
from pyiur.auth import OAuth1

from pyiur.types import Account
from pyiur.types import Credits
from pyiur.types import Image
from pyiur.types import Statistics as Stats

from pyiur.exceptions import InsufficientCreditsError

try:
    import json
except ImportError:
    import simplejson as json

_Undef = object()

def _requires_auth(func):

    @functools.wraps(func)
    def wrapped(self, *args, **kwargs):
        assert not isinstance(self.auth, AnonAuth), (
            'Authentication required to call {0}.'.format(func.__name__))
        return func(self, *args, **kwargs)

    return wrapped

def _requires_account(func):

    @functools.wraps(func)
    def wrapped(self, *args, **kwargs):
        assert type(self.auth) not in (AnonAuth, DevAuth), (
            'Account authentication required to call {0}.'
            .format(func.__name__))
        return func(self, *args, **kwargs)

    return wrapped

class Imgur(object):
    """


    """

    _API_URL = 'https://api.imgur.com/2/{0}.json'

    def __init__(self, auth = None, **kwargs):
        if isinstance(auth, basestring):
            auth = DevAuth(auth)
        elif not auth and 'key' in kwargs and 'secret' not in kwargs:
            auth = DevAuth(kwargs['key'])
        elif not auth and 'key' in kwargs and 'secret' in kwargs:
            auth = OAuth1(kwargs['key'], kwargs['secret'])
        elif not auth and 'username' in kwargs and 'password' in kwargs:
            auth = CookieAuth(kwargs['username'], kwargs['password'])

        self.auth = auth or AnonAuth()

    @property
    def credits(self):

        def parse_credit(content):
            credits = json.loads(content)['credits']
            limit = credits['limit']
            remaining = credits['remaining']
            reset = datetime.datetime.fromtimestamp(credits['reset'])
            refresh_in_secs = credits['refresh_in_secs']
            return Credits(limit, remaining, reset, refresh_in_secs)

        response = requests.get(self._api('credits'), **self.auth.update())
        self._validate(response)

        return parse_credit(response.content) 

    @property
    @_requires_auth
    def statistics(self):

        def parse_stats(content):
            stats = json.loads(content)['stats']
            most_popular_images = tuple(stats['most_popular_images'])
            images_uploaded = stats['images_uploaded']
            images_viewed = stats['images_veiwed']
            bandwidth_used = stats['bandwidth_used']
            average_image_size = stats['average_image_size']
            return Stats(most_popular_images, images_uploaded, images_viewed,
                         bandwidth_used, average_image_size)

        response = requests.get(self._api('stats'), **self.auth.update())
        self._validate(response)

        return parse_stats(response.content)

    stats = statistics

    @property
    @_requires_account
    def account(self):

        def parse_account(content):
            account = json.loads(content)['account']
            url = account['url']
            is_pro = account['is_pro'] == 'true'
            default_album_privacy = account['default_album_privacy']
            public_images = account['public_images'] == 'true'
            return Account(url, is_pro, default_album_privacy, public_images)

        response = requests.get(self._api('account'), **self.auth.update())
        self._validate(response)

        return parse_account(response.content)

    @_requires_account
    def get_images(self, count = None, page = None):
        # TODO
        pass

    @property
    @_requires_account
    def images_count(self):
        # TODO
        pass

    @_requires_account
    def get_albums(self, count = None, page = None):
        # TODO
        pass

    @property
    @_requires_account
    def albums_count(self):
        # TODO
        pass

    def sideload(self, url):
        params = {'url': url}
        response = requests.get(self._api('upload'),
                                **self.auth.update(params))
        self._validate(response)

        return self._parse_image(response.content)

    @_requires_auth
    def upload_url(self, url, type = None, name = None, title = None,
                   caption = None):
        # TODO
        pass

    @_requires_auth
    def upload_file(self, filename, type = None, name = None, title = None,
                    caption = None):
        # TODO
        pass

    @_requires_auth
    def delete_image(self, image_or_delete_hash):
        # TODO
        pass

    @_requires_account
    def delete_album(self, album_or_delete_hash):
        # TODO
        pass

    @_requires_account
    def set_album_order(self, *album_ids):
        # TODO
        pass

    @_requires_account
    def create_album(self, title = None, description = None, privacy = None,
                     layout = None):
        # TODO
        pass

    @_requires_account
    def set_image_order(self, album_or_hash, *image_ids):
        # TODO
        pass

    def _validate(self, response):
        """"""

        def validate_credits():
            credits = self.get_credits()

            if credits.remaining <= 0:
                minutes = credits.refresh_in_secs / 60
                seconds = credits.refresh_in_secs % 60
                raise InsufficientCreditsError(
                    'There are insufficient credits to perform the requested '
                    'action. Credits will be refreshed in {0} minute{1} and '
                    '{2} second{3}.'.format(minutes,
                                            '' if minutes == 1 else 's',
                                            seconds,
                                            '' if seconds == 1 else 's'))


        if response.status_code == 403:
            validate_credits()

        # TODO

    def _parse_image(self, content):
        # TODO
        return Image()

    def _api(self, *args, **kwargs):
        """Convenience method for formatting JSON API URLs."""

        return self._API_URL.format(*args, **kwargs)


def sideload(url, auth = None, **kwargs):
    return Imgur(auth, **kwargs).sideload(url)

def get_credits(auth = None, **kwargs):
    return Imgur(auth, **kwargs).credits

def get_statistics(auth = None, **kwargs):
    return Imgur(auth, **kwargs).statistics

def get_account(auth = None, **kwargs):
    return Imgur(auth, **kwargs).account

get_stats = get_statistics


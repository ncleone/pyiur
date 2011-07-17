# -*- coding: utf-8 -*-
"""


"""

import collections
import datetime
import os.path

import dateutil.parser
import requests

from pyiur.auth import Anonymous as AnonAuth
from pyiur.auth import Cookie as CookieAuth
from pyiur.auth import DeveloperKey as DevAuth
from pyiur.auth import OAuth1

from pyiur.exceptions import ActionNotSupportedError
from pyiur.exceptions import ImgurException
from pyiur.exceptions import ImgurServerError
from pyiur.exceptions import InsufficientCreditsError
from pyiur.exceptions import PermissionDeniedError
from pyiur.exceptions import ServiceTemporarilyDownError

try:
    import json
except ImportError:
    import simplejson as json

#==============================================================================
# Information
#==============================================================================
def get_stats(view = None):
    """
    
    
    """

    def parse_stats(content):
        """"""

        stats = json.loads(content)['stats']
        most_popular_images = tuple(stats['most_popular_images'])
        images_uploaded = stats['images_uploaded']
        images_viewed = stats['images_veiwed']
        bandwidth_used = stats['bandwidth_used']
        average_image_size = stats['average_image_size']
        return Statistics(most_popular_images, images_uploaded, images_viewed,
                          bandwidth_used, average_image_size)

    params = None if not view else {'view': view}
    response = requests.get(_api('stats'), params)
    _validate(response)

    return parse_stats(response.content)

def get_credits(auth = None):
    """
    
    
    """

    def parse_credits(content):
        """"""

        credits = json.loads(content)['credits']
        limit = credits['limit']
        remaining = credits['remaining']
        reset = datetime.datetime.fromtimestamp(credits['reset'])
        refresh_in_secs = credits['refresh_in_secs']
        return Credits(limit, remaining, reset, refresh_in_secs)

    auth = _parse_auth(auth)
    response = requests.get(_api('credits'), **auth.update())
    _validate(response, auth)

    return parse_credits(response.content)

def get_account(auth = None):
    """
    
    
    """

    def parse_account(content):
        """"""

        account = json.loads(content)['account']
        url = account['url']
        is_pro = account['is_pro'] == 'true'
        default_album_privacy = account['default_album_privacy']
        public_images = account['public_images'] == 'true'
        return Account(url, is_pro, default_album_privacy, public_images)

    auth = _parse_auth(auth)
    response = requests.get(_api('account'), **auth.update())
    _validate(response)

    return parse_account(response.content)

#==============================================================================
# Images
#==============================================================================
def sideload(url, auth = None):
    """
    
    
    """

    auth = _parse_auth(auth)
    params = {'url': url}
    response = requests.get(_api('upload'), **auth.update(params))
    _validate(response)

    return _parse_image(response.content)

def upload_url(url, auth, name = None, title = None, caption = None):
    """
    
    
    """

    auth = _parse_auth(auth)
    params = {'image': url, 'type': 'url'}

    if name:
        params['name'] = name

    if title:
        params['title'] = title

    if caption:
        params['caption'] = caption

    response = requests.post(_api('upload'), **auth.update(params))
    _validate(response)

    return _parse_image(response.content)

def upload_file(filename, auth, title = None, caption = None):
    """
    
    
    """

    auth = _parse_auth(auth)

    with open(filename, 'rb') as file:
        params = {'type': 'file', 'name': os.path.basename(filename)}

        if title:
            params['title'] = title

        if caption:
            params['caption'] = caption

        response = requests.post(_api('upload'), files = {'image': file},
                                 **auth.update(params))
        _validate(response)

        return _parse_image(response.content)

def get_image(hash):
    """
    
    
    """

    response = requests.get(_api('image', hash))
    _validate(response)

    return _parse_image(response.content)

def delete_image(hash):
    """
    
    
    """

    response = requests.delete(_api('delete', hash))
    _validate(response)

def get_images(auth, count = None, page = None):

    """
    
    
    """

    # TODO
    pass

def get_images_count(auth):
    """
    
    
    """

    def parse_count(content):
        """"""

        images_count = json.loads(content)['images_count']
        count = images_count['count']
        return count

    auth = _parse_auth(auth)
    response = requests.get(_api('account', 'images_count'), **auth.update())
    _validate(response)

    return parse_count(response.content)

#==============================================================================
# Albums
#==============================================================================
def get_albums_count(auth):
    """
    
    
    """

    def parse_count(content):
        """"""

        albums_count = json.loads(content)['albums_count']
        count = albums_count['count']
        return count

    auth = _parse_auth(auth)
    response = requests.get(_api('account/albums_count'), **auth.update())
    _validate(response)

    return parse_count(response.content)

def get_albums(auth, count = None, page = None):

    """
    
    
    """

    # TODO
    pass



def delete_album(hash, auth = None):
    """
    
    
    """

    # TODO
    pass


def set_album_order(album_ids, auth = None):
    """
    
    
    """

    # TODO
    pass


def create_album(auth, title = None, description = None, privacy = None,
                 layout = None):
    """
    
    
    """

    # TODO
    pass


def set_image_order(album_hash, image_ids, auth = None):
    """
    
    
    """

    # TODO
    pass

#==============================================================================
# Types
#==============================================================================
Credits = collections.namedtuple('Credits', ('limit', 'remaining', 'reset',
                                             'refresh_in_secs'))

Statistics = collections.namedtuple('Statistics',
                                    ('most_popular_images', 'images_uploaded',
                                     'images_viewed', 'bandwidth_used',
                                     'average_image_size'))

Account = collections.namedtuple('Account', ('url', 'is_pro',
                                             'default_album_privacy',
                                             'public_images'))

Image = collections.namedtuple('Image', ('hash', 'delete_hash', 'type', 'name',
                                         'title', 'caption', 'datetime',
                                        'animated', 'width', 'height', 'size',
                                        'views', 'bandwidth', 'links'))

class StatsViews(object):
    TODAY = 'today'
    WEEK = 'week'
    MONTH = 'month'

class Album(object):
    pass

#==============================================================================
# Private Helpers
#==============================================================================
def _parse_auth(auth):

    def dev_auth():
        if isinstance(auth, basestring):
            return DevAuth(auth)

    def cookie_auth():
        try:
            username, password = auth
            return CookieAuth(username, password)
        except (ValueError, TypeError):
            pass

    return dev_auth() or cookie_auth() or auth or AnonAuth()


def _validate(response, auth = None):
    """"""

    def validate_credits():
        """"""

        credits = get_credits(auth)

        if credits.remaining <= 0:
            raise InsufficientCreditsError(credits)

    if response.status_code == 200:
        return

    if response.status_code == 400:
        error = json.loads(response.content)['error']

        if error['method'] == 'delete':
            return

        raise Exception # TODO

    if response.status_code == 403:
        validate_credits()
        raise PermissionDeniedError

    if response.status_code == 404:
        raise ActionNotSupportedError

    if response.status_code == 500:
        raise ImgurServerError

    if response.status_code == 503:
        raise ServiceTemporarilyDownError

    raise ImgurException(u'imgur replied with an unexpected status code '
                         '{0} and the following content:\n\n{1}'
                         .format(response.status_code, response.content))

def _parse_image(content):
    """"""

    raw = json.loads(content)
    data = next(raw.itervalues())
    image = data['image']
    links = data['links']

    dt = dateutil.parser.parse(image['datetime'])
    animated = image['animated'] == 'true'

    return Image(image['hash'], image['deletehash'], image['type'],
                 image['name'], image['title'], image['caption'], dt, animated,
                 image['width'], image['height'], image['size'],
                 image['views'], image['bandwidth'], links)

def _api(*args):
    """Convenience method for formatting JSON API URLs."""

    params = '/'.join(args)
    return 'https://api.imgur.com/2/{0}.json'.format(params)

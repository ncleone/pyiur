# -*- coding: utf-8 -*-
"""


"""

import collections
import datetime
import functools
import os.path

import dateutil.parser
import requests

from pyiur.auth import Anonymous as _AnonAuth
from pyiur.auth import Cookie as _CookieAuth
from pyiur.auth import DeveloperKey as _DevAuth
from pyiur.auth import OAuth1 as oauth

from pyiur.exceptions import ActionNotSupportedError
from pyiur.exceptions import ImgurException
from pyiur.exceptions import ImgurServerError
from pyiur.exceptions import ImgurTemporarilyDownError
from pyiur.exceptions import InsufficientCreditsError
from pyiur.exceptions import PermissionDeniedError

try:
    import json
except ImportError:
    import simplejson as json

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

Album = collections.namedtuple('Album', ('id', 'title', 'description',
                                         'privacy', 'cover', 'order', 'layout',
                                         'datetime', 'link', 'anonymous_link'))

class AlbumPrivacy(object):
    PUBLIC = 'public'
    HIDDEN = 'hidden'
    SECRET = 'secret'

class AlbumLayout(object):
    BLOG = 'blog'
    HORIZONTAL = 'horizontal'
    VERTICAL = 'vertical'
    GRID = 'grid'

class StatsView(object):
    TODAY = 'today'
    WEEK = 'week'
    MONTH = 'month'

#==============================================================================
# Information
#==============================================================================
def get_stats(view = None, auth = None):
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

    auth = _parse_auth(auth)
    params = None if not view else {'view': view}
    response = requests.get(_api('stats'), **auth.update(params))
    _validate_response(response)

    return parse_stats(response.content)

get_stats_today = functools.partial(get_stats, StatsView.TODAY)
get_stats_week = functools.partial(get_stats, StatsView.WEEK)
get_stats_month = functools.partial(get_stats, StatsView.MONTH)

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
    _validate_response(response, auth)

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
    _validate_response(response)

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
    _validate_response(response)

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
    _validate_response(response)

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
        _validate_response(response)

        return _parse_image(response.content)

def get_image(hash, auth = None):
    """
    
    
    """

    auth = _parse_auth(auth)
    response = requests.get(_api('image', hash), **auth.update())
    _validate_response(response)

    return _parse_image(response.content)

def delete_image(hash, auth = None):
    """
    
    
    """

    auth = _parse_auth(auth)
    response = requests.delete(_api('delete', hash), **auth.update())
    _validate_response(response)

def get_images(auth, count = None, page = None):
    """
    
    
    """

    params = {}

    if count:
        params['count'] = count

    if page:
        params['page'] = page

    auth = _parse_auth(auth)
    response = requests.get(_api('account', 'images'), **auth.update(params))
    _validate_response(response)

    return _parse_images(response.content)

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
    _validate_response(response)

    return parse_count(response.content)

def update_image(hash, auth, **fields_to_update):
    """


    """

    params = {}

    if 'title' in fields_to_update:
        params['title'] = fields_to_update['title']

    if 'caption' in fields_to_update:
        params['caption'] = fields_to_update['caption']

    auth = _parse_auth(auth)
    response = requests.post(_api('account', 'images', hash),
                             **auth.update(params))
    _validate_response(response)

    return _parse_image(response.content)

def set_image_title(hash, title, auth):
    """
    
    
    """

    return update_image(hash, title = title, auth = auth)

def set_image_caption(hash, caption, auth):
    """
    
    
    """

    return update_image(hash, caption = caption, auth = auth)

#==============================================================================
# Albums
#==============================================================================
def get_albums(auth, count = None, page = None):
    """
    
    
    """

    params = {}

    if count:
        params['count'] = count

    if page:
        params['page'] = page

    auth = _parse_auth(auth)
    response = requests.get(_api('account', 'albums'), **auth.update(params))
    _validate_response(response)

    return _parse_albums(response.content)

def get_albums_count(auth):
    """
    
    
    """

    def parse_count(content):
        """"""

        albums_count = json.loads(content)['albums_count']
        count = albums_count['count']
        return count

    auth = _parse_auth(auth)
    response = requests.get(_api('account', 'albums_count'), **auth.update())
    _validate_response(response)

    return parse_count(response.content)

def create_album(auth, title = None, description = None, privacy = None,
                 layout = None):
    """


    """

    params = {}

    if title:
        params['title'] = title

    if description:
        params['description'] = description

    if privacy:
        params['privacy'] = privacy

    if layout:
        params['layout'] = layout

    auth = _parse_auth(auth)
    response = requests.post(_api('account', 'albums'), **auth.update(params))
    _validate_response(response)

    return _parse_album(response.content)

def delete_album(id, auth):
    """


    """

    auth = _parse_auth(auth)
    response = requests.delete(_api('account', 'albums', id), **auth.update())
    _validate_response(response)

def set_albums_order(ids, auth):
    """


    """

    # TODO
    pass

def get_album_images(id, auth, count = None, page = None):
    """


    """

    params = {}

    if count:
        params['count'] = count

    if page:
        params['page'] = page

    auth = _parse_auth(auth)
    response = requests.get(_api('account', 'albums', id),
                            **auth.update(params))
    _validate_response(response)

    return _parse_images(response.content)

def set_album_images_order(id, image_hashes, auth):
    """


    """

    # TODO
    pass

def update_album(id, auth, **params):
    """


    """

    # TODO
    pass

def set_album_title(id, title, auth):
    """
    
    
    """

    return update_album(id, title = title, auth = auth)

def set_album_description(id, description, auth):
    """
    
    
    """

    return update_album(id, description = description, auth = auth)

def set_album_cover(id, hash, auth):
    """
    
    
    """

    return update_album(id, cover = hash, auth = auth)

def set_album_privacy(id, privacy, auth):
    """
    
    
    """

    return update_album(id, privacy = privacy, auth = auth)

def set_album_layout(id, layout, auth):
    """
    
    
    """

    return update_album(id, layout = layout, auth = auth)

def set_album_images(id, hashes, auth):
    """
    
    
    """

    return update_album(id, images = hashes, auth = auth)

def add_album_images(id, hashes, auth):
    """
    
    
    """

    return update_album(id, add_images = hashes, auth = auth)

def remove_album_images(id, hashes, auth):
    """
    
    
    """

    return update_album(id, del_images = hashes, auth = auth)

#==============================================================================
# Private Helpers
#==============================================================================
def _parse_auth(auth):
    """


    """

    def dev_auth():
        """"""

        if isinstance(auth, basestring):
            return _DevAuth(auth)

    def cookie_auth():
        """"""

        try:
            username, password = auth
            return _CookieAuth(username, password)
        except (ValueError, TypeError):
            pass

    return dev_auth() or cookie_auth() or auth or _AnonAuth()


def _validate_response(response, auth = None):
    """"""

    def validate_credits():
        """"""

        credits = get_credits(auth)

        if credits.remaining <= 0:
            raise InsufficientCreditsError(credits)

    if response.status_code == 200:
        return

    if response.status_code == 403:
        validate_credits()
        error = json.loads(response.content)['error']
        raise PermissionDeniedError(error['message'])

    if response.status_code in (400, 404):
        error = json.loads(response.content)['error']

        if error['method'] == 'delete':
            return

        raise ActionNotSupportedError(error['message'])

    if response.status_code == 500:
        raise ImgurServerError

    if response.status_code == 503:
        raise ImgurTemporarilyDownError

    raise ImgurException(u'imgur replied with an unexpected status code '
                         '{0} and the following content:\n\n{1}'
                         .format(response.status_code, response.content))

def _parse_image(content):
    """


    """

    def get_already_decoded():
        """"""

        if not isinstance(content, basestring):
            return content['image'], content.get('links')

    def decode():
        """"""

        raw = json.loads(content)
        data = next(raw.itervalues())
        return data['image'], data.get('links')

    image, links = get_already_decoded() or decode()
    dt = dateutil.parser.parse(image['datetime'])
    animated = image['animated'] == 'true'

    return Image(image['hash'], image.get('deletehash'), image['type'],
                 image.get('name'), image['title'], image['caption'], dt,
                 animated, image['width'], image['height'], image['size'],
                 image['views'], image['bandwidth'], links)

def _parse_images(content):
    """


    """

    raw = json.loads(content)
    data = next(raw.itervalues())
    return [_parse_image(image) for image in data]

def _parse_album(content):
    """


    """

    def get_already_decoded():
        """"""

        if not isinstance(content, basestring):
            return content

    def decode():
        """"""

        return json.loads(content)['albums']

    album = get_already_decoded() or decode()
    dt = dateutil.parser.parse(album['datetime'])

    return Album(album['id'], album['title'], album['description'],
                 album['privacy'], album['cover'], album['order'],
                 album['layout'], dt, album['link'],
                 album['anonymous_link'])

def _parse_albums(content):
    """


    """

    albums = json.loads(content)['albums']
    return sorted((_parse_album(album) for album in albums),
                  key = lambda k: k.order)

def _api(*args):
    """Convenience method for formatting Imgur JSON API URLs."""

    return 'https://api.imgur.com/2/{0}.json'.format('/'.join(args))

# -*- coding: utf-8 -*-
"""


"""

from __future__ import with_statement

import datetime
import os.path
import sys
import urlparse

import dateutil.parser
import requests

try:
    import json
except ImportError:
    import simplejson as json

from pyiur.auth import Authenticatable as _Authenticatable

from pyiur.exceptions import ActionNotSupportedError
from pyiur.exceptions import ImgurException
from pyiur.exceptions import ImgurServerError
from pyiur.exceptions import ImgurTemporarilyDownError
from pyiur.exceptions import InsufficientCreditsError
from pyiur.exceptions import PermissionDeniedError

#==============================================================================
# Types
#==============================================================================
class Credits(object):
    """


    """

    def __init__(self, limit, remaining, reset, refresh_in_secs):
        self.limit = limit
        self.remaining = remaining
        self.reset = reset
        self.refresh_in_secs = refresh_in_secs


class Statistics(object):
    """


    """

    _IMAGE_URI = 'http://imgur.com/%s'

    def __init__(self, most_popular_images, images_uploaded, images_viewed,
                 bandwidth_used, average_image_size):
        """


        """

        self.most_popular_images = most_popular_images
        self.images_uploaded = images_uploaded
        self.images_viewed = images_viewed
        self.bandwidth_used = bandwidth_used
        self.average_image_size = average_image_size


def Account(object):
    """


    """

    def __init__(self, url, is_pro, default_album_privacy, public_images):
        """


        """

        self.url = url
        self.is_pro = is_pro
        self.default_album_privacy = default_album_privacy
        self.is_images_public = public_images


class Resource(object):
    """


    """

    def __init__(self, url):
        """
        """

        self.url = url

    @property
    def resource(self):
        """
        """

        path = urlparse.urlsplit(self.url).path
        resource = os.path.basename(path)
        return resource

    filename = resource

    def download(self, filename = None):
        """
        """

        def get_save_filename():
            path = filename or self.filename

            if not os.path.lexists(path):
                return path

            root, ext = os.path.splitext(path)

            for i in xrange(1, sys.maxint):
                next_path = u'%s (%d)%s' % (root, i, ext)

                if not os.path.lexists(next_path):
                    return next_path

        response = requests.get(self.url)

        if response.status_code != 200:
            raise ImgurException() # TODO

        with open(get_save_filename(), 'wb') as resource_file:
            resource_file.write(response.content)


class Image(_Authenticatable):
    """


    """

    def __init__(self, hash, type, title, caption, datetime, animated, width,
                 height, size, views, bandwidth, links, name = None,
                 delete_hash = None, auth = None):

        def set_resource(attr):
            """"""

            url = links.get(attr)
            link = Resource(url) if url else None

            setattr(self, attr, link)

        self.auth = auth
        self.hash = hash
        self.delete_hash = delete_hash
        self.type = type
        self.name = name
        self.title = title
        self.caption = caption
        self.datetime = datetime
        self.animated = animated
        self.width = width
        self.height = height
        self.size = size
        self.views = views
        self.bandwidth = bandwidth
        self.links = links

        set_resource('imgur_page')
        set_resource('delete_page')

        set_resource('original')
        set_resource('huge_thumbnail')
        set_resource('large_thumbnail')
        set_resource('medium_thumbnail')
        set_resource('small_thumbnail')
        set_resource('big_square')
        set_resource('small_square')

    @property
    def filename(self):
        if self.name:
            ext = os.path.splitext(self.original.url)[1]
            return self.name + ext

        return self.original.filename

    def _get_title(self):
        return self._title

    def _set_title(self, value):
        self._title = value
        self._title_changed = True

    title = property(_get_title, _set_title)

    def download(self, filename = None):
        """


        """

        return self.original.download(filename or self.filename)

    def delete(self):
        """


        """

        Imgur(self.auth).delete_image(self.hash)

    def save(self):
        """


        """

        # TODO


class Album(_Authenticatable):
    """


    """

    class PrivacyOptions(object):
        PUBLIC = 'public'
        HIDDEN = 'hidden'
        SECRET = 'secret'


    class LayoutOptions(object):
        BLOG = 'blog'
        HORIZONTAL = 'horizontal'
        VERTICAL = 'vertical'
        GRID = 'grid'


    def __init__(self, id, title, description, privacy, cover, order, layout,
                 datetime, link, anonymous_link, auth = None):
        """


        """

        self.auth = auth
        self.id = id
        self.title = title
        self.description = description
        self.privacy = privacy
        self.cover = cover
        self.order = order
        self.layout = layout
        self.datetime = datetime
        self.link = link
        self.anonymous_link = anonymous_link

    def get_images(self, count = None, page = None):
        """


        """

        return Imgur(self.auth).get_album_images(self.id, count, page)

    @property
    def images(self):
        """


        """

        for page in xrange(1, sys.maxint):
            try:
                page_images = self.get_images(page = page)
            except ActionNotSupportedError:
                raise StopIteration

            for image in page_images:
                yield image

    @property
    def num_images(self):
        """


        """

        return len(list(self.images))

    def download(self, folder = None):
        """


        """

        for image in self.images:
            image.download(folder)

    def delete(self):
        """


        """

        Imgur(self.auth).delete_album(self.id)


class Imgur(_Authenticatable):
    """


    """

    def __init__(self, auth = None):
        """


        """

        self.auth = auth

    #==========================================================================
    # Informational
    #==========================================================================
    @property
    def stats_for_today(self):
        """


        """

        return self._get_stats('today')

    @property
    def stats_for_week(self):
        """


        """

        return self._get_stats('week')

    @property
    def stats_for_month(self):
        """


        """

        return self._get_stats('month')

    @property
    def credits(self):
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

        response = requests.get(self._api('credits'), **self.auth.update())
        self._validate_response(response)

        return parse_credits(response.content)

    @property
    def account(self):
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

        response = requests.get(self._api('account'), **self.auth.update())
        self._validate_response(response)

        return parse_account(response.content)

    def _get_stats(self, view = None):
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
            return Statistics(most_popular_images, images_uploaded,
                              images_viewed, bandwidth_used,
                              average_image_size)

        params = None if not view else {'view': view}
        response = requests.get(self._api('stats'), **self.auth.update(params))
        self._validate_response(response)

        return parse_stats(response.content)

    #==========================================================================
    # Images
    #==========================================================================
    def sideload(self, url):
        """
        
        
        """

        params = {'url': url}
        response = requests.get(self._api('upload'),
                                **self.auth.update(params))
        self._validate_response(response)

        return self._parse_image(response.content)

    def upload_url(self, url, name = None, title = None, caption = None):
        """
        
        
        """

        params = {'image': url, 'type': 'url'}

        if name:
            params['name'] = name

        if title:
            params['title'] = title

        if caption:
            params['caption'] = caption

        response = requests.post(self._api('upload'),
                                 **self.auth.update(params))
        self._validate_response(response)

        return self._parse_image(response.content)

    def upload_file(self, filename, title = None, caption = None):
        """
        
        
        """

        with open(filename, 'rb') as file:
            params = {'type': 'file', 'name': os.path.basename(filename)}

            if title:
                params['title'] = title

            if caption:
                params['caption'] = caption

            response = requests.post(self._api('upload'),
                                     files = {'image': file},
                                     **self.auth.update(params))
            self._validate_response(response)

            return self._parse_image(response.content)

    def get_image(self, hash):
        """


        """

        response = requests.get(self._api('image', hash), **self.auth.update())
        self._validate_response(response)

        return self._parse_image(response.content)

    def delete_image(self, hash):
        """


        """

        response = requests.delete(self._api('delete', hash),
                                   **self.auth.update())
        self._validate_response(response)

    def get_images(self, count = None, page = None):
        """


        """

        params = {}

        if count:
            params['count'] = count

        if page:
            params['page'] = page

        response = requests.get(self._api('account', 'images'),
                                **self.auth.update(params))
        self._validate_response(response)

        return self._parse_images(response.content)

    @property
    def images(self):
        """Yields all images for the authenticated account."""

        for page in xrange(1, sys.maxint):
            try:
                page_images = self.get_images(page = page)
            except ActionNotSupportedError:
                raise StopIteration

            for image in page_images:
                yield image

    @property
    def num_images(self):
        """
        
        
        """

        def parse_count(content):
            """"""

            images_count = json.loads(content)['images_count']
            count = images_count['count']
            return count

        response = requests.get(self._api('account', 'images_count'),
                                **self.auth.update())
        self._validate_response(response)

        return parse_count(response.content)

    def set_image_title(self, hash, title):
        """


        """

        params = {'title': title}
        response = requests.post(self._api('account', 'images', hash),
                                 **self.auth.update(params))
        self._validate_response(response)

        return self._parse_image(response.content)

    def set_image_caption(self, hash, caption):
        """


        """

        params = {'caption': caption}
        response = requests.post(self._api('account', 'images', hash),
                                 **self.auth.update(params))
        self._validate_response(response)

        return self._parse_image(response.content)

    def _parse_image(self, content):
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

        return Image(image['hash'], image['type'], image['title'],
                     image['caption'], dt, animated, image['width'],
                     image['height'], image['size'], image['views'],
                     image['bandwidth'], links, image.get('name'),
                     image.get('deletehash'), self.auth)

    def _parse_images(self, content):
        """


        """

        raw = json.loads(content)
        data = next(raw.itervalues())
        return [self._parse_image(image) for image in data]

    #==========================================================================
    # Albums
    #==========================================================================
    def get_albums(self, count = None, page = None):
        """


        """

        params = {}

        if count:
            params['count'] = count

        if page:
            params['page'] = page

        response = requests.get(self._api('account', 'albums'),
                                **self.auth.update(params))
        self._validate_response(response)

        return self._parse_albums(response.content)


    @property
    def albums(self):
        """Yields all albums for the authenticated account."""

        for page in xrange(1, sys.maxint):
            try:
                page_albums = self.get_albums(page = page)
            except ActionNotSupportedError:
                raise StopIteration

            for album in page_albums:
                yield album

    @property
    def num_albums(self):
        """


        """

        def parse_count(content):
            """"""

            albums_count = json.loads(content)['albums_count']
            count = albums_count['count']
            return count

        response = requests.get(self._api('account', 'albums_count'),
                                **self.auth.update())
        self._validate_response(response)

        return parse_count(response.content)

    def get_album_image_count(self, id):
        """
        """

        return len(list(self.get_album_images(id)))

    def _parse_album(self, content):
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
                     album['anonymous_link'], self.auth)

    def _parse_albums(self, content):
        """


        """

        albums = json.loads(content)['albums']
        return sorted((self._parse_album(album) for album in albums),
                      key = lambda k: k.order)

    #==========================================================================
    # Common
    #==========================================================================
    def _api(self, *args):
        """Convenience method for formatting Imgur JSON API URLs."""

        return 'https://api.imgur.com/2/%s.json' % '/'.join(args)

    def _validate_response(self, response):
        """"""

        def validate_credits():
            """"""

            if self.credits.remaining <= 0:
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
                             '%s and the following content:\n\n%s' %
                             (response.status_code, response.content))


    def create_album(self, title = None, description = None, privacy = None,
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

        response = requests.post(self._api('account', 'albums'),
                                 **self.auth.update(params))
        self._validate_response(response)

        return self._parse_album(response.content)

    def delete_album(self, id):
        """


        """

        response = requests.delete(self._api('account', 'albums', id),
                                   **self.auth.update())
        self._validate_response(response)

    def get_album_images(self, id, count = None, page = None):
        """


        """

        params = {}

        if count:
            params['count'] = count

        if page:
            params['page'] = page

        response = requests.get(self._api('account', 'albums', id),
                                **self.auth.update(params))
        self._validate_response(response)

        return self._parse_images(response.content)

#def set_albums_order(ids, auth):
#    """
#
#
#    """
#
#    # TODO
#    pass
#
#def set_album_images_order(id, image_hashes, auth):
#    """
#
#
#    """
#
#    # TODO
#    pass
#
#def update_album(id, auth, **params):
#    """
#
#
#    """
#
#    # TODO
#    pass
#
#def set_album_title(id, title, auth):
#    """
#    
#    
#    """
#
#    return update_album(id, title = title, auth = auth)
#
#def set_album_description(id, description, auth):
#    """
#    
#    
#    """
#
#    return update_album(id, description = description, auth = auth)
#
#def set_album_cover(id, hash, auth):
#    """
#    
#    
#    """
#
#    return update_album(id, cover = hash, auth = auth)
#
#def set_album_privacy(id, privacy, auth):
#    """
#    
#    
#    """
#
#    return update_album(id, privacy = privacy, auth = auth)
#
#def set_album_layout(id, layout, auth):
#    """
#    
#    
#    """
#
#    return update_album(id, layout = layout, auth = auth)
#
#def set_album_images(id, hashes, auth):
#    """
#    
#    
#    """
#
#    return update_album(id, images = hashes, auth = auth)
#
#def add_album_images(id, hashes, auth):
#    """
#    
#    
#    """
#
#    return update_album(id, add_images = hashes, auth = auth)
#
#def remove_album_images(id, hashes, auth):
#    """
#    
#    
#    """
#
#    return update_album(id, del_images = hashes, auth = auth)
#

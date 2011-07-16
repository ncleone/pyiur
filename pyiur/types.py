# -*- coding: utf-8 -*-
"""


"""

import collections

Credits = collections.namedtuple('Credits', ('limit', 'remaining', 'reset',
                                             'refresh_in_secs'))

Statistics = collections.namedtuple('Statistics',
                                    ('most_popular_images', 'images_uploaded',
                                     'images_viewed', 'bandwidth_used',
                                     'average_image_size'))

Account = collections.namedtuple('Account', ('url', 'is_pro',
                                             'default_album_privacy',
                                             'public_images'))

class Image(object):
    pass



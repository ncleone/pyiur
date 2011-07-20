#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Example use of pyiur to extract all original images from an authenticated
imgur.com account.

"""

from __future__ import with_statement

import getpass

import pyiur
import requests

if __name__ == '__main__':
    # Authenticate with imgur.com using cookie authentication.
    username = raw_input('imgur.com username: ')
    password = getpass.getpass('imgur.com password: ')
    imgur = pyiur.Imgur(auth = (username, password))

    # Get the number of images to show progess while downloading.
    # Save it, because imgur.num_images represents the number of images on the
    # server, which may change as we download images.
    num_images = imgur.num_images

    # Loop over all of the images and count them.
    for i, image in enumerate(imgur.images):
        # Download the image.
        print u'(%s/%s) Downloading image %s...' % (i + 1, num_images,
                                                    image.filename),
        response = requests.get(image.original_url)

        if response.status_code == 200:
            # Download succeeded; let's save this thing!
            with open(image.filename, 'wb') as image_file:
                image_file.write(response.content)

            print 'DONE'
        else:
            # Oh noes!
            print 'FAILED'


#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Example use of pyiur to extract all original images from an authenticated
imgur.com account.

"""

import getpass

import pyiur

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

        try:
            image.download()
            print 'DONE'
        except:
            print 'FAILED'

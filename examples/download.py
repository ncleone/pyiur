#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Example use of pyiur to extract all original images from an authenticated
imgur.com account.

"""

import getpass

import pyiur
import requests

def image_links(auth):
    """Yields all original image links for the authenticated user."""

    # We can't get all images at once, so we need to get each page of images.
    num_pages = pyiur.get_images_pages(auth = auth)

    for page in xrange(1, num_pages + 1):
        # Gets the images for the current page and yields the link to the
        # original image back to the caller.
        #
        # Note: I like to put auth at the back, so I always pass it by name.
        page_images = pyiur.get_images(page = page, auth = auth)
 
        for image in page_images:
            yield image.links['original']

def download_images(auth):
    """Downloads and saves all of the images for the authenticated user."""

    # Create an iterator that yields all of the image links.
    links = image_links(auth = auth)

    # Get the number of images to give a nicer downloading message.
    count = pyiur.get_images_count(auth = auth)

    # Let's loop over all of the links to the original images.
    for i, url in enumerate(links, 1):
        # Use the resource image name for our file.
        filename = url.rsplit('/')[-1]

        # Time to download the image.
        print u'({1}/{2}) Downloading image {0}...'.format(filename, i, count),
        response = requests.get(url)

        if response.status_code == 200:
            # Download succeeded; let's save this thing!
            with open(filename, 'wb') as image_file:
                image_file.write(response.content)

            print 'DONE'
        else:
            # Oh noes!
            print 'FAILED'

if __name__ == '__main__':
    username = raw_input('imgur.com username: ')
    password = getpass.getpass('imgur.com password: ')

    download_images(auth = (username, password))

# -*- coding: utf-8 -*-
"""


"""

import pyiur.core

def get_stats_for_today():
    """


    """

    return pyiur.core.Imgur().stats_for_today

def get_stats_for_week():
    """


    """

    return pyiur.core.Imgur().stats_for_week

def get_stats_for_month():
    """


    """

    return pyiur.core.Imgur().stats_for_month

def get_credits():
    """


    """

    return pyiur.core.Imgur().credits

def get_image(hash):
    """


    """

    return pyiur.core.Imgur().get_image(hash)

def sideload(url):
    """


    """

    return pyiur.core.Imgur().sideload(url)

# -*- coding: utf-8 -*-
"""


"""

class InsufficientCreditsError(Exception):
    """


    """

    def __init__(self, credits):
        minutes = credits.refresh_in_secs / 60
        seconds = credits.refresh_in_secs % 60

        super(self.__class__, self).__init__(
            'There are insufficient credits to perform the requested action. '
            'Credits will be refreshed in {0} minute{1} and {2} second{3}.'
            .format(minutes, '' if minutes == 1 else 's',
                    seconds, '' if seconds == 1 else 's'))

class InvalidCredentialsError(Exception):
    """


    """



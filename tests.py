# -*- coding: utf-8 -*-
"""


"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import pyiur

class ImgurTests(unittest.TestCase):

    def test_get_stats(self):
        stats = pyiur.get_stats()

        assert isinstance(stats.most_popular_images, tuple)
        assert isinstance(stats.images_uploaded, int)
        assert isinstance(stats.images_viewed, int)
        assert isinstance(stats.bandwidth_used, basestring)
        assert isinstance(stats.average_image_size, basestring)

        month_stats = pyiur.get_stats('month')
        self.assertEqual(stats, month_stats)

    def test_get_stats_today(self):
        stats = pyiur.get_stats_today()
        today_stats = pyiur.get_stats('today')

        self.assertEqual(stats, today_stats)

    def test_get_stats_week(self):
        stats = pyiur.get_stats_week()
        week_stats = pyiur.get_stats('week')

        self.assertEqual(stats, week_stats)

    def test_get_stats_month(self):
        stats = pyiur.get_stats_month()
        month_stats = pyiur.get_stats('month')

        self.assertEqual(stats, month_stats)


if __name__ == '__main__':
    unittest.main()

from unittest import TestCase

from typing import List

class CustomTests(TestCase):
    def assert_equal(self, first, second, msg = None):
        self.assertEqual(first, second, msg)

    def assert_list_equal(self, first: List, second: List, msg: str = None):
        self.assertListEqual(first, second, msg)

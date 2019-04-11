# -*- coding: utf-8 -*-

import unittest
from cronexp._field import parse_field


class ParseFieldTest(unittest.TestCase):
    def test_all(self):
        self.assertEqual(
                parse_field('*', 0, 10),
                [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    def test_single(self):
        self.assertEqual(
                parse_field('5', 0, 10),
                [5])

    def test_range(self):
        self.assertEqual(
                parse_field('2-6', 0, 10),
                [2, 3, 4, 5, 6])

    def test_step_all(self):
        self.assertEqual(
                parse_field('*/3', 0, 10),
                [0, 3, 6, 9])

    def test_step_begin(self):
        self.assertEqual(
                parse_field('1/3', 0, 10),
                [1, 4, 7, 10])

    def test_step_range(self):
        self.assertEqual(
                parse_field('1-9/3', 0, 10),
                [1, 4, 7])

# -*- coding: utf-8 -*-

import itertools
import unittest
from cronexp._field import Field


class FieldTest(unittest.TestCase):
    def test_field(self):
        selected = [2, 3, 5, 7]
        field = Field('2,3,5,7', 0, 10)
        self.assertFalse(field.is_any)
        for i in range(0, 12):
            with self.subTest(i=i):
                self.assertEqual(field.is_selected(i), i in selected)

    def test_any(self):
        field = Field('*', 0, 10)
        self.assertTrue(field.is_any)
        for i in range(0, 12):
            with self.subTest(i=i):
                self.assertEqual(field.is_selected(i), 0 <= i <= 10)

    def test_next(self):
        field = Field('5,8', 0, 10)
        for i in range(0, 11):
            with self.subTest(i=i):
                result = field.next(i)
                if i < 5:
                    self.assertEqual(result.value, 5)
                    self.assertFalse(result.move_up)
                elif 5 <= i < 8:
                    self.assertEqual(result.value, 8)
                    self.assertFalse(result.move_up)
                else:
                    self.assertEqual(result.value, 5)
                    self.assertTrue(result.move_up)

    def test_next_greater_than_max(self):
        field = Field('1', 0, 10)
        result = field.next(11)
        self.assertEqual(result.value, 1)
        self.assertTrue(result.move_up)

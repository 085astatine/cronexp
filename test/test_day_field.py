# -*- coding: utf-8 -*-

import unittest
from cronexp._day_field import day_of_month_l, day_of_month_w


class DayOfMonthLTest(unittest.TestCase):
    def test_l(self):
        year = 2019
        month = 2
        for day in range(1, 31 + 1):
            with self.subTest(year=year, month=month, day=day):
                self.assertEqual(
                        day_of_month_l(year, month, day),
                        28 if day < 28 else None)


class DayOfMonthWTest(unittest.TestCase):
    def test_weekday(self):
        target = 14
        year = 2019
        month = 2
        for day in range(1, 31 + 1):
            result = target
            with self.subTest(year=year, month=month, day=day):
                self.assertEqual(
                        day_of_month_w(target, year, month, day),
                        result if result > day else None)

    def test_saturday(self):
        target = 23
        year = 2019
        month = 11
        for day in range(1, 31 + 1):
            result = 22
            with self.subTest(year=year, month=month, day=day):
                self.assertEqual(
                        day_of_month_w(target, year, month, day),
                        result if result > day else None)

    def test_sunday(self):
        target = 11
        year = 2019
        month = 8
        for day in range(1, 31 + 1):
            result = 12
            with self.subTest(year=year, month=month, day=day):
                self.assertEqual(
                        day_of_month_w(target, year, month, day),
                        result if result > day else None)

    def test_1st(self):
        target = 1
        year = 2019
        month = 6
        for day in range(1, 31 + 1):
            result = 3
            with self.subTest(year=year, month=month, day=day):
                self.assertEqual(
                        day_of_month_w(target, year, month, day),
                        result if result > day else None)

    def test_last(self):
        target = 31
        year = 2019
        month = 3
        for day in range(1, 31 + 1):
            result = 29
            with self.subTest(year=year, month=month, day=day):
                self.assertEqual(
                        day_of_month_w(target, year, month, day),
                        result if result > day else None)

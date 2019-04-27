# -*- coding: utf-8 -*-

import calendar
import datetime
import itertools
import math
import unittest
from cronexp._field import weekday_word_set
from cronexp._weekday_field import day_of_week_l, day_of_week_sharp


class DayOfWeekLTest(unittest.TestCase):
    def test_l(self):
        year = 2019
        last_weekday_list = {
                'sun': [27, 24, 31, 28, 26, 30, 28, 25, 29, 27, 24, 29],
                'mon': [28, 25, 25, 29, 27, 24, 29, 26, 30, 28, 25, 30],
                'tue': [29, 26, 26, 30, 28, 25, 30, 27, 24, 29, 26, 31],
                'wed': [30, 27, 27, 24, 29, 26, 31, 28, 25, 30, 27, 25],
                'thu': [31, 28, 28, 25, 30, 27, 25, 29, 26, 31, 28, 26],
                'fri': [25, 22, 29, 26, 31, 28, 26, 30, 27, 25, 29, 27],
                'sat': [26, 23, 30, 27, 25, 29, 27, 31, 28, 26, 30, 28]}
        for name, weekday in weekday_word_set().items():
            for month, day in itertools.product(
                    range(1, 13),
                    (None, *range(1, 32))):
                result = last_weekday_list[name][month - 1]
                self.assertEqual(
                        calendar.weekday(year, month, result),
                        (weekday - 1) % 7)
                with self.subTest(
                        weekday=name,
                        year=year,
                        month=month,
                        day=day):
                    self.assertEqual(
                            day_of_week_l(weekday, year, month, day),
                            result if day is None or day < result else None)


class DayOfWeekSharpTest(unittest.TestCase):
    def test_sharp(self):
        year = 2019
        first_weekday_list = {
                'sun': [6, 3, 3, 7, 5, 2, 7, 4, 1, 6, 3, 1],
                'mon': [7, 4, 4, 1, 6, 3, 1, 5, 2, 7, 4, 2],
                'tue': [1, 5, 5, 2, 7, 4, 2, 6, 3, 1, 5, 3],
                'wed': [2, 6, 6, 3, 1, 5, 3, 7, 4, 2, 6, 4],
                'thu': [3, 7, 7, 4, 2, 6, 4, 1, 5, 3, 7, 5],
                'fri': [4, 1, 1, 5, 3, 7, 5, 2, 6, 4, 1, 6],
                'sat': [5, 2, 2, 6, 4, 1, 6, 3, 7, 5, 2, 7]}
        for (name, weekday), week_number in itertools.product(
                weekday_word_set().items(),
                range(1, 6)):
            for month, day in itertools.product(
                    range(1, 13),
                    (None, *range(1, 32))):
                result = (
                        first_weekday_list[name][month - 1]
                        + 7 * (week_number - 1))
                lastday = calendar.monthrange(year, month)[1]
                if lastday < result:
                    result = None
                else:
                    self.assertEqual(
                            calendar.weekday(year, month, result),
                            (weekday - 1) % 7)
                with self.subTest(
                        weekday=name,
                        week_number=week_number,
                        year=year,
                        month=month,
                        day=day):
                    expected = (
                        None if result is None
                        else result if day is None or day < result
                        else None)
                    self.assertEqual(
                            day_of_week_sharp(
                                    weekday,
                                    week_number,
                                    year,
                                    month,
                                    day),
                            expected)

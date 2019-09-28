# -*- coding: utf-8 -*-

import calendar
import datetime
import itertools
import math
import unittest
from cronexp._field_parser import FieldParseError, weekday_word_set
from cronexp._weekday_field import (
        DayOfWeekField, SundayMode, day_of_week_l, day_of_week_hash)


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
            for month in range(1, 13):
                expected = last_weekday_list[name][month - 1]
                with self.subTest(
                        weekday=name,
                        year=year,
                        month=month):
                    self.assertEqual(
                            calendar.weekday(year, month, expected),
                            (weekday - 1) % 7)
                    self.assertEqual(
                            day_of_week_l(weekday, year, month),
                            expected)


class DayOfWeekHashTest(unittest.TestCase):
    def test_hash(self):
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
            for month in range(1, 13):
                expected = (
                        first_weekday_list[name][month - 1]
                        + 7 * (week_number - 1))
                lastday = calendar.monthrange(year, month)[1]
                if lastday < expected:
                    expected = None
                else:
                    self.assertEqual(
                            calendar.weekday(year, month, expected),
                            (weekday - 1) % 7)
                with self.subTest(
                        weekday=name,
                        week_number=week_number,
                        year=year,
                        month=month):
                    self.assertEqual(
                            day_of_week_hash(
                                    weekday,
                                    week_number,
                                    year,
                                    month),
                            expected)


class DayOfWeekFieldTest(unittest.TestCase):
    def test_normal(self):
        field = DayOfWeekField(
                'Mon,Wed,Fri',
                non_standard=False,
                use_word_set=True)
        year = 2019
        init_date = datetime.date(year, 1, 1)
        expected_list = list(
                filter(lambda date: date.weekday() in [0, 2, 4],
                       map(lambda i: init_date + datetime.timedelta(days=i),
                           range(0, 365))))
        for month, day in itertools.product(
                range(1, 13),
                (None, *range(1, 32))):
            expected = min(
                    map(lambda date: date.day,
                        filter(lambda date: (
                                    date.month == month
                                    and (day is None or day < date.day)),
                               expected_list)),
                    default=None)
            with self.subTest(year=year, month=month, day=day):
                self.assertEqual(field.next(year, month, day), expected)

    def test_blank(self):
        field = DayOfWeekField('?', non_standard=True, use_word_set=True)
        self.assertTrue(field.is_blank)
        self.assertEqual(field.next(2019, 1, 1), None)

    def test_l(self):
        field = DayOfWeekField(
                'MonL,ThuL',
                non_standard=True,
                use_word_set=True)
        year = 2019
        expected_table = [
                [28, 31],  # 2019/01
                [25, 28],  # 2019/02
                [25, 28],  # 2019/03
                [25, 29],  # 2019/04
                [27, 30],  # 2019/05
                [24, 27],  # 2019/06
                [25, 29],  # 2019/07
                [26, 29],  # 2019/08
                [26, 30],  # 2019/09
                [28, 31],  # 2019/10
                [25, 28],  # 2019/11
                [26, 30]]  # 2019/12
        for month, day in itertools.product(
                range(1, 13),
                (None, *range(1, 32))):
            expected = min(
                    filter(lambda x: day is None or day < x,
                           expected_table[month - 1]),
                    default=None)
            with self.subTest(year=year, month=month, day=day):
                self.assertEqual(field.next(year, month, day), expected)

    def test_hash(self):
        field = DayOfWeekField(
                'Mon#1,Fri#1,Tue#2,Thu#2,Wed#3,Sun#4,Sat#4,Mon#5,Fri#5',
                non_standard=True,
                use_word_set=True)
        year = 2019
        expected_table = [
                [4, 7, 8, 10, 16, 26, 27],  # 2019/01
                [1, 4, 12, 14, 20, 23, 24],  # 2019/02
                [1, 4, 12, 14, 20, 23, 24, 29],  # 2019/03
                [1, 5, 9, 11, 17, 27, 28, 29],  # 2019/04
                [3, 6, 9, 14, 15, 25, 26, 31],  # 2019/05
                [3, 7, 11, 13, 19, 22, 23],  # 2019/06
                [1, 5, 9, 11, 17, 27, 28, 29],  # 2019/07
                [2, 5, 8, 13, 21, 24, 25, 30],  # 2019/08
                [2, 6, 10, 12, 18, 22, 28, 30],  # 2019/09
                [4, 7, 8, 10, 16, 26, 27],  # 2019/10
                [1, 4, 12, 14, 20, 23, 24, 29],  # 2019/11
                [2, 6, 10, 12, 18, 22, 28, 30]]  # 2019/12
        for month, day in itertools.product(
                range(1, 13),
                (None, *range(1, 32))):
            expected = min(
                    filter(lambda x: day is None or day < x,
                           expected_table[month - 1]),
                    default=None)
            with self.subTest(year=year, month=month, day=day):
                self.assertEqual(field.next(year, month, day), expected)

    def test_next(self):
        field = DayOfWeekField(
                'Sun,Sat#2,Sat#4,FriL',
                non_standard=True,
                use_word_set=True)
        year = 2019
        expected_table = [
                [6, 12, 13, 20, 25, 26, 27],  # 2019/01
                [3, 9, 10, 17, 22, 23, 24],  # 2019/02
                [3, 9, 10, 17, 23, 24, 29, 31],  # 2019/03
                [7, 13, 14, 21, 26, 27, 28],  # 2019/04
                [5, 11, 12, 19, 25, 26, 31],  # 2019/05
                [2, 8, 9, 16, 22, 23, 28, 30],  # 2019/06
                [7, 13, 14, 21, 26, 27, 28],  # 2019/07
                [4, 10, 11, 18, 24, 25, 30],  # 2019/08
                [1, 8, 14, 15, 22, 27, 28, 29],  # 2019/09
                [6, 12, 13, 20, 25, 26, 27],  # 2019/10
                [3, 9, 10, 17, 23, 24, 29],  # 2019/11
                [1, 8, 14, 15, 22, 27, 28, 29]]  # 2019/12
        for month, day in itertools.product(
                range(1, 13),
                (None, *range(1, 32))):
            expected = min(
                    filter(lambda x: day is None or day < x,
                           expected_table[month - 1]),
                    default=None)
            with self.subTest(year=year, month=month, day=day):
                self.assertEqual(field.next(year, month, day), expected)

    def test_error_disuse_word_set(self):
        with self.assertRaises(FieldParseError):
            field = DayOfWeekField(
                    'Mon',
                    non_standard=True,
                    use_word_set=False)

    def test_sunday_mode(self):
        expression = [
                ('0', '7'),
                ('0,6', '6-7'),
                ('Sun-Sat', 'Mon-Sun')]
        for sun_is_0, sun_is_7 in expression:
            with self.subTest(sun_is_0=sun_is_0, sun_is_7=sun_is_7):
                field_0 = DayOfWeekField(
                        sun_is_0,
                        non_standard=True,
                        sunday_mode=SundayMode.SUNDAY_IS_0)
                with self.assertRaises(FieldParseError):
                    field_7 = DayOfWeekField(
                            sun_is_7,
                            non_standard=True,
                            sunday_mode=SundayMode.SUNDAY_IS_0)
                field_7 = DayOfWeekField(
                        sun_is_7,
                        non_standard=True,
                        sunday_mode=SundayMode.SUNDAY_IS_7)
                year = 2019
                for month, day in itertools.product(
                        range(1, 13),
                        (None, *range(1, 32))):
                    with self.subTest(year=year, month=month, day=day):
                        self.assertEqual(
                                field_0.next(year, month, day),
                                field_7.next(year, month, day))

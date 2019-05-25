# -*- coding: utf-8 -*-

import calendar
import itertools
import math
import unittest
from cronexp._dayexp import Dayexp, DayexpParseError, DaySelectionMode


class DayexpTest(unittest.TestCase):
    def test_every_day(self):
        for mode in [DaySelectionMode.AND, DaySelectionMode.OR]:
            dayexp = Dayexp('*', '*', selection_mode=mode)
            year = 2019
            for month, day in itertools.product(
                    range(1, 13),
                    (None, *range(1, 32))):
                lastday = calendar.monthrange(year, month)[1]
                expected = (1 if day is None
                            else day + 1 if day < lastday
                            else None)
                with self.subTest(mode=mode, year=year, month=month, day=day):
                    self.assertEqual(dayexp.next(year, month, day), expected)
                    if expected is not None:
                        self.assertTrue(
                                dayexp.is_selected(year, month, expected))

    def test_day_only(self):
        for mode in [DaySelectionMode.AND, DaySelectionMode.OR]:
            dayexp = Dayexp('*/5', '*', selection_mode=mode)
            year = 2019
            for month, day in itertools.product(
                    range(1, 13),
                    (None, *range(1, 32))):
                lastday = calendar.monthrange(year, month)[1]
                expected = math.ceil(day / 5) * 5 + 1 if day is not None else 1
                if expected > lastday:
                    expected = None
                with self.subTest(mode=mode, year=year, month=month, day=day):
                    self.assertEqual(dayexp.next(year, month, day), expected)
                    if expected is not None:
                        self.assertTrue(
                                dayexp.is_selected(year, month, expected))

    def test_weekday_only(self):
        for mode in [DaySelectionMode.AND, DaySelectionMode.OR]:
            dayexp = Dayexp('*', 'Mon,Wed,Fri', selection_mode=mode)
            year = 2019
            for month, day in itertools.product(
                    range(1, 13),
                    (None, *range(1, 32))):
                init_weekday, lastday = calendar.monthrange(year, month)
                selected_weekday = (0, 2, 4)
                if day is None:
                    expected = min(1 + (i - init_weekday) % 7
                                   for i in selected_weekday)
                elif day < lastday:
                    weekday = calendar.weekday(year, month, day)
                    expected = min(
                            filter(lambda x: x <= lastday,
                                   [day + 7 - (weekday - i) % 7
                                    for i in selected_weekday]),
                            default=None)
                else:
                    expected = None
                with self.subTest(mode=mode, year=year, month=month, day=day):
                    self.assertEqual(dayexp.next(year, month, day), expected)
                    if expected is not None:
                        self.assertTrue(
                                dayexp.is_selected(year, month, expected))

    def test_day_or_weekday(self):
        dayexp = Dayexp(
                '*/5',
                'Mon,Wed,Fri',
                selection_mode=DaySelectionMode.OR)
        year = 2019
        for month, day in itertools.product(
                range(1, 13),
                (None, *range(1, 32))):
            init_weekday, lastday = calendar.monthrange(year, month)
            selected_weekday = (0, 2, 4)
            target = []
            if day is None:
                target.append(1)
                target.extend(1 + (i - init_weekday) % 7
                              for i in selected_weekday)
            elif day < lastday:
                weekday = calendar.weekday(year, month, day)
                target.append(math.ceil(day / 5) * 5 + 1)
                target.extend(day + 7 - (weekday - i) % 7
                              for i in selected_weekday)
            expected = min(
                    filter(lambda x: x <= lastday, target),
                    default=None)
            with self.subTest(year=year, month=month, day=day):
                self.assertEqual(dayexp.next(year, month, day), expected)
                if expected is not None:
                    self.assertTrue(dayexp.is_selected(year, month, expected))

    def test_day_and_weekday(self):
        dayexp = Dayexp(
                '*/5',
                'Mon,Wed,Fri',
                selection_mode=DaySelectionMode.AND)
        year = 2019
        for month, day in itertools.product(
                range(1, 13),
                (None, *range(1, 32))):
            lastday = calendar.monthrange(year, month)[1]
            selected_weekday = (0, 2, 4)
            expected = None
            for i in itertools.count(
                    start=math.ceil(day / 5) * 5 + 1 if day is not None else 1,
                    step=5):
                if i > lastday:
                    break
                if calendar.weekday(year, month, i) in selected_weekday:
                    expected = i
                    break
            with self.subTest(year=year, month=month, day=day):
                self.assertEqual(dayexp.next(year, month, day), expected)
                if expected is not None:
                    self.assertTrue(dayexp.is_selected(year, month, expected))

    def test_day_only_non_standard(self):
        dayexp = Dayexp(
                '10-22/3,1W,10W,16W,22W,31W,L',
                '?',
                selection_mode=DaySelectionMode.EITHER)
        year = 2019
        expected_table = [
                [1, 10, 13, 16, 19, 22, 31],  # 2019/01
                [1, 10, 11, 13, 15, 16, 19, 22, 28],  # 2019/02
                [1, 10, 11, 13, 15, 16, 19, 22, 29, 31],  # 2019/03
                [1, 10, 13, 16, 19, 22, 30],  # 2019/04
                [1, 10, 13, 16, 19, 22, 31],  # 2019/05
                [3, 10, 13, 16, 17, 19, 21, 22, 28, 30],  # 2019/06
                [1, 10, 13, 16, 19, 22, 31],  # 2019/07
                [1, 9, 10, 13, 16, 19, 22, 30, 31],  # 2019/08
                [2, 10, 13, 16, 19, 22, 23, 30],  # 2019/09
                [1, 10, 13, 16, 19, 22, 31],  # 2019/10
                [1, 10, 11, 13, 15, 16, 19, 22, 29, 30],  # 2019/11
                [2, 10, 13, 16, 19, 22, 23, 31]]  # 2019/12
        for month, day in itertools.product(
                range(1, 13),
                (None, *range(1, 32))):
            expected = min(
                    filter(lambda x: day is None or x > day,
                           expected_table[month - 1]),
                    default=None)
            with self.subTest(year=year, month=month, day=day):
                self.assertEqual(dayexp.next(year, month, day), expected)
                if expected is not None:
                    self.assertTrue(dayexp.is_selected(year, month, expected))

    def test_weekday_only_non_standard(self):
        dayexp = Dayexp(
                '?',
                'Sun,Sat#2,Sat#4,FriL,SatL',
                selection_mode=DaySelectionMode.EITHER)
        year = 2019
        expected_table = [
                [6, 12, 13, 20, 25, 26, 27],  # 2019/01
                [3, 9, 10, 17, 22, 23, 24],  # 2019/02
                [3, 9, 10, 17, 23, 24, 29, 30, 31],  # 2019/03
                [7, 13, 14, 21, 26, 27, 28],  # 2019/04
                [5, 11, 12, 19, 25, 26, 31],  # 2019/05
                [2, 8, 9, 16, 22, 23, 28, 29, 30],  # 2019/06
                [7, 13, 14, 21, 26, 27, 28],  # 2019/07
                [4, 10, 11, 18, 24, 25, 30, 31],  # 2019/08
                [1, 8, 14, 15, 22, 27, 28, 29],  # 2019/09
                [6, 12, 13, 20, 25, 26, 27],  # 2019/10
                [3, 9, 10, 17, 23, 24, 29, 30],  # 2019/11
                [1, 8, 14, 15, 22, 27, 28, 29]]  # 2019/12
        for month, day in itertools.product(
                range(1, 13),
                (None, *range(1, 32))):
            expected = min(
                    filter(lambda x: day is None or x > day,
                           expected_table[month - 1]),
                    default=None)
            with self.subTest(year=year, month=month, day=day):
                self.assertEqual(dayexp.next(year, month, day), expected)
                if expected is not None:
                    self.assertTrue(dayexp.is_selected(year, month, expected))

    def test_error_one_must_be_question(self):
        input_list = [
                ('1-7', 'Mon'),
                ('?', '?')]
        for day, weekday in input_list:
            with self.subTest(day=day, weekday=weekday):
                with self.assertRaises(DayexpParseError):
                    dayexp = Dayexp(
                            day,
                            weekday,
                            selection_mode=DaySelectionMode.EITHER)

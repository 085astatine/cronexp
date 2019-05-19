# -*- coding: utf-8 -*-

import calendar
import itertools
import math
import unittest
from cronexp._dayexp import Dayexp, DaySelectionMode


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

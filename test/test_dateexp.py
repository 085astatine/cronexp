# -*- coding: utf-8 -*-

import calendar
import datetime
import math
import unittest
from cronexp._dateexp import Dateexp
from cronexp._dayexp import DaySelectionMode


class DateexpTest(unittest.TestCase):
    def test_every_day(self):
        for day_selection_mode in [DaySelectionMode.AND, DaySelectionMode.OR]:
            dateexp = Dateexp(
                    day='*',
                    month='*',
                    weekday='*',
                    day_selection_mode=day_selection_mode)
            init_date = datetime.date(year=2019, month=1, day=1)
            for total_days in range(0, 365 + 1):
                date = init_date + datetime.timedelta(days=total_days)
                next_date = date + datetime.timedelta(days=1)
                with self.subTest(
                        year=date.year,
                        month=date.month,
                        day=date.day,
                        day_selection_mode=day_selection_mode):
                    result = dateexp.next(
                            year=date.year,
                            month=date.month,
                            day=date.day)
                    self.assertEqual(result.day, next_date.day)
                    self.assertEqual(result.month, next_date.month)
                    self.assertEqual(result.year, next_date.year)

    def test_every_month(self):
        for day_selection_mode in [DaySelectionMode.AND, DaySelectionMode.OR]:
            dateexp = Dateexp(
                    day='10',
                    month='*',
                    weekday='*',
                    day_selection_mode=day_selection_mode)
            init_date = datetime.date(year=2019, month=1, day=1)
            for total_days in range(0, 365 + 1):
                date = init_date + datetime.timedelta(days=total_days)
                if date.day < 10:
                    next_month = date.month
                    next_year = date.year
                elif date.month < 12:
                    next_month = date.month + 1
                    next_year = date.year
                else:
                    next_month = 1
                    next_year = date.year + 1
                with self.subTest(
                        year=date.year,
                        month=date.month,
                        day=date.day,
                        day_selection_mode=day_selection_mode):
                    result = dateexp.next(
                            year=date.year,
                            month=date.month,
                            day=date.day)
                    self.assertEqual(result.day, 10)
                    self.assertEqual(result.month, next_month)
                    self.assertEqual(result.year, next_year)

    def test_yearly(self):
        for day_selection_mode in [DaySelectionMode.AND, DaySelectionMode.OR]:
            dateexp = Dateexp(
                    day='2',
                    month='4',
                    weekday='*',
                    day_selection_mode=day_selection_mode)
            init_date = datetime.date(year=2019, month=1, day=1)
            for total_days in range(0, 365 + 1):
                date = init_date + datetime.timedelta(days=total_days)
                next_year = date.year
                if date.month > 4 or (date.month == 4 and date.day >= 2):
                    next_year += 1
                with self.subTest(
                        year=date.year,
                        month=date.month,
                        day=date.day,
                        day_selection_mode=day_selection_mode):
                    result = dateexp.next(
                            year=date.year,
                            month=date.month,
                            day=date.day)
                    self.assertEqual(result.day, 2)
                    self.assertEqual(result.month, 4)
                    self.assertEqual(result.year, next_year)

    def test_every_weekday(self):
        for day_selection_mode in [DaySelectionMode.AND, DaySelectionMode.OR]:
            weekday_list = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            for weekday_index, weekday in enumerate(weekday_list):
                dateexp = Dateexp(
                        day='*',
                        month='*',
                        weekday=weekday,
                        day_selection_mode=day_selection_mode)
                init_date = datetime.date(year=2019, month=1, day=1)
                for total_days in range(0, 365 + 1):
                    date = init_date + datetime.timedelta(days=total_days)
                    delta_day = 7 - (date.weekday() - weekday_index) % 7
                    next_date = date + datetime.timedelta(days=delta_day)
                    with self.subTest(
                            weekday=weekday,
                            year=date.year,
                            month=date.month,
                            day=date.day,
                            day_selection_mode=day_selection_mode):
                        result = dateexp.next(
                                year=date.year,
                                month=date.month,
                                day=date.day)
                        self.assertEqual(next_date.weekday(), weekday_index)
                        self.assertEqual(result.day, next_date.day)
                        self.assertEqual(result.month, next_date.month)
                        self.assertEqual(result.year, next_date.year)

    def test_next(self):
        for day_selection_mode in [DaySelectionMode.AND, DaySelectionMode.OR]:
            dateexp = Dateexp(
                    day='*/10',
                    month='*/3',
                    weekday='*',
                    day_selection_mode=day_selection_mode)
            init_date = datetime.date(year=2019, month=1, day=1)
            for total_days in range(0, 365 + 1):
                date = init_date + datetime.timedelta(days=total_days)
                if date.month % 3 != 1:
                    next_day = 1
                    next_month = math.ceil(date.month / 3) * 3 + 1
                    next_year = date.year
                    if next_month > 12:
                        next_month %= 12
                        next_year += 1
                else:
                    next_day = math.ceil(date.day / 10) * 10 + 1
                    next_month = date.month
                    next_year = date.year
                    last_day = calendar.monthrange(date.year, date.month)[1]
                    if next_day > last_day:
                        next_day = 1
                        next_month += 3
                        if next_month > 12:
                            next_month %= 12
                            next_year += 1
                next_date = datetime.date(
                        year=next_year,
                        month=next_month,
                        day=next_day)
                with self.subTest(
                        year=date.year,
                        month=date.month,
                        day=date.day,
                        day_selection_mode=day_selection_mode):
                    result = dateexp.next(
                            year=date.year,
                            month=date.month,
                            day=date.day)
                    self.assertEqual(result.day, next_date.day)
                    self.assertEqual(result.month, next_date.month)
                    self.assertEqual(result.year, next_date.year)

    def test_day_or_weekday(self):
        dateexp = Dateexp(
                day='*/5',
                month='*',
                weekday='Fri',
                day_selection_mode=DaySelectionMode.OR)
        init_date = datetime.date(year=2019, month=1, day=1)
        for total_days in range(0, 365 + 1):
            date = init_date + datetime.timedelta(days=total_days)
            last_day = calendar.monthrange(date.year, date.month)[1]
            delta_day = min(
                    7 - (date.weekday() - 4) % 7,
                    5 - (date.day - 1) % 5
                    if math.ceil(date.day / 5) * 5 + 1 <= last_day
                    else 1 + last_day - date.day)
            next_date = date + datetime.timedelta(days=delta_day)
            with self.subTest(year=date.year, month=date.month, day=date.day):
                result = dateexp.next(
                        year=date.year,
                        month=date.month,
                        day=date.day)
                self.assertEqual(result.day, next_date.day)
                self.assertEqual(result.month, next_date.month)
                self.assertEqual(result.year, next_date.year)

    def test_day_and_weekday(self):
        dateexp = Dateexp(
                day='*/5',
                month='*',
                weekday='Fri',
                day_selection_mode=DaySelectionMode.AND)
        init_date = datetime.date(year=2019, month=1, day=1)
        for total_days in range(0, 365 + 1):
            date = init_date + datetime.timedelta(days=total_days)
            next_date = date
            while True:
                last_day = calendar.monthrange(
                        next_date.year,
                        next_date.month)[1]
                delta_day = (
                        5 - (next_date.day - 1) % 5
                        if math.ceil(next_date.day / 5) * 5 + 1 <= last_day
                        else 1 + last_day - next_date.day)
                next_date = next_date + datetime.timedelta(days=delta_day)
                if next_date.weekday() == 4:
                    break
            with self.subTest(year=date.year, month=date.month, day=date.day):
                result = dateexp.next(
                        year=date.year,
                        month=date.month,
                        day=date.day)
                self.assertEqual(result.day, next_date.day)
                self.assertEqual(result.month, next_date.month)
                self.assertEqual(result.year, next_date.year)

    def test_first_weekday(self):
        weekday_list = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for weekday_index, weekday in enumerate(weekday_list):
            dateexp = Dateexp(
                    day='1-7',
                    month='*',
                    weekday=weekday,
                    day_selection_mode=DaySelectionMode.AND)
            init_date = datetime.date(year=2019, month=1, day=1)
            for total_days in range(0, 365 + 1):
                date = init_date + datetime.timedelta(days=total_days)
                next_year = date.year
                next_month = date.month
                next_day = date.day
                while True:
                    init_weekday = calendar.monthrange(
                            next_year,
                            next_month)[0]
                    first_day = 1 + (weekday_index - init_weekday) % 7
                    if next_day is None or first_day > next_day:
                        next_date = datetime.date(
                                year=next_year,
                                month=next_month,
                                day=first_day)
                        break
                    next_month += 1
                    next_day = None
                    if next_month > 12:
                        next_month %= 12
                        next_year += 1
                with self.subTest(
                        weekday=weekday,
                        year=date.year,
                        month=date.month,
                        day=date.day):
                    result = dateexp.next(
                            year=date.year,
                            month=date.month,
                            day=date.day)
                    self.assertEqual(next_date.weekday(), weekday_index)
                    self.assertEqual(result.day, next_date.day)
                    self.assertEqual(result.month, next_date.month)
                    self.assertEqual(result.year, next_date.year)

    def test_error_nonexistent_date(self):
        for day_selection_mode in [DaySelectionMode.AND, DaySelectionMode.OR]:
            with self.subTest(day_selection_mode=day_selection_mode):
                dateexp = Dateexp(
                        day='30',
                        month='2',
                        weekday='*',
                        day_selection_mode=day_selection_mode)
                with self.assertRaises(RecursionError):
                    dateexp.next(day=1, month=1, year=2019)

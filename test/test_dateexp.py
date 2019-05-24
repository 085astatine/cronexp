# -*- coding: utf-8 -*-

import calendar
import datetime
import math
import unittest
from cronexp._dateexp import Dateexp
from cronexp._dayexp import DaySelectionMode
from cronexp._field_parser import FieldParseError


class DateexpTest(unittest.TestCase):
    def test_every_day(self):
        dateexp_list = {
                'and': Dateexp(
                        '*', '*', '*',
                        day_selection_mode=DaySelectionMode.AND),
                'or': Dateexp(
                        '*', '*', '*',
                        day_selection_mode=DaySelectionMode.OR),
                'day_only': Dateexp(
                        '*', '*', '?',
                        day_selection_mode=DaySelectionMode.EITHER),
                'weekday_only': Dateexp(
                        '?', '*', '*',
                        day_selection_mode=DaySelectionMode.EITHER)}
        for mode, dateexp in dateexp_list.items():
            init_date = datetime.date(year=2019, month=1, day=1)
            for delta_day in range(0, 365 + 1):
                date = init_date + datetime.timedelta(days=delta_day)
                next_date = date + datetime.timedelta(days=1)
                with self.subTest(
                        mode=mode,
                        year=date.year,
                        month=date.month,
                        day=date.day):
                    result = dateexp.next(
                            year=date.year,
                            month=date.month,
                            day=date.day)
                    self.assertEqual(result.day, next_date.day)
                    self.assertEqual(result.month, next_date.month)
                    self.assertEqual(result.year, next_date.year)

    def test_every_month(self):
        dateexp_list = {
                'and': Dateexp(
                        '10', '*', '*',
                        day_selection_mode=DaySelectionMode.AND),
                'or': Dateexp(
                        '10', '*', '*',
                        day_selection_mode=DaySelectionMode.OR),
                'day_only': Dateexp(
                        '10', '*', '?',
                        day_selection_mode=DaySelectionMode.EITHER)}
        for mode, dateexp in dateexp_list.items():
            init_date = datetime.date(year=2019, month=1, day=1)
            for delta_day in range(0, 365 + 1):
                date = init_date + datetime.timedelta(days=delta_day)
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
                        mode=mode,
                        year=date.year,
                        month=date.month,
                        day=date.day):
                    result = dateexp.next(
                            year=date.year,
                            month=date.month,
                            day=date.day)
                    self.assertEqual(result.day, 10)
                    self.assertEqual(result.month, next_month)
                    self.assertEqual(result.year, next_year)

    def test_yearly(self):
        dateexp_list = {
                'and': Dateexp(
                        '2', '4', '*',
                        day_selection_mode=DaySelectionMode.AND),
                'or': Dateexp(
                        '2', '4', '*',
                        day_selection_mode=DaySelectionMode.OR),
                'day_only': Dateexp(
                        '2', '4', '?',
                        day_selection_mode=DaySelectionMode.EITHER)}
        for mode, dateexp in dateexp_list.items():
            init_date = datetime.date(year=2019, month=1, day=1)
            for delta_day in range(0, 365 + 1):
                date = init_date + datetime.timedelta(days=delta_day)
                next_year = date.year
                if date.month > 4 or (date.month == 4 and date.day >= 2):
                    next_year += 1
                with self.subTest(
                        mode=mode,
                        year=date.year,
                        month=date.month,
                        day=date.day):
                    result = dateexp.next(
                            year=date.year,
                            month=date.month,
                            day=date.day)
                    self.assertEqual(result.day, 2)
                    self.assertEqual(result.month, 4)
                    self.assertEqual(result.year, next_year)

    def test_every_weekday(self):
        weekday_list = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for weekday_index, weekday in enumerate(weekday_list):
            dateexp_list = {
                    'and': Dateexp(
                            '*', '*', weekday,
                            day_selection_mode=DaySelectionMode.AND),
                    'or': Dateexp(
                            '*', '*', weekday,
                            day_selection_mode=DaySelectionMode.OR),
                    'weekday_only': Dateexp(
                            '?', '*', weekday,
                            day_selection_mode=DaySelectionMode.EITHER)}
            for mode, dateexp in dateexp_list.items():
                init_date = datetime.date(year=2019, month=1, day=1)
                for delta_day in range(0, 365 + 1):
                    date = init_date + datetime.timedelta(days=delta_day)
                    delta_day = 7 - (date.weekday() - weekday_index) % 7
                    next_date = date + datetime.timedelta(days=delta_day)
                    with self.subTest(
                            mode=mode,
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

    def test_next(self):
        dateexp_list = {
                'and': Dateexp(
                        '*/10', '*/3', '*',
                        day_selection_mode=DaySelectionMode.AND),
                'or': Dateexp(
                        '*/10', '*/3', '*',
                        day_selection_mode=DaySelectionMode.OR),
                'day_only': Dateexp(
                        '*/10', '*/3', '?',
                        day_selection_mode=DaySelectionMode.EITHER)}
        for mode, dateexp in dateexp_list.items():
            init_date = datetime.date(year=2019, month=1, day=1)
            for delta_day in range(0, 365 + 1):
                date = init_date + datetime.timedelta(days=delta_day)
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
                        mode=mode,
                        year=date.year,
                        month=date.month,
                        day=date.day):
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
        for delta_day in range(0, 365 + 1):
            date = init_date + datetime.timedelta(days=delta_day)
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
        for delta_day in range(0, 365 + 1):
            date = init_date + datetime.timedelta(days=delta_day)
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
            dateexp_list = {
                    'and': Dateexp(
                            '1-7', '*', weekday,
                            day_selection_mode=DaySelectionMode.AND),
                    'weekday_only': Dateexp(
                            '?', '*', '{0}#1'.format(weekday),
                            day_selection_mode=DaySelectionMode.EITHER)}
            for mode, dateexp in dateexp_list.items():
                init_date = datetime.date(year=2019, month=1, day=1)
                for delta_day in range(0, 365 + 1):
                    date = init_date + datetime.timedelta(days=delta_day)
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
                            mode=mode,
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

    def test_error_disuse_word_set(self):
        input_list = [
                ('Jan', 'Mon'),
                ('Jan', '1'),
                ('1', 'Mon')]
        for mode in DaySelectionMode:
            for month, weekday in input_list:
                with self.assertRaises(FieldParseError):
                    field = Dateexp(
                            '?' if mode is DaySelectionMode.EITHER else '*',
                            month,
                            weekday,
                            day_selection_mode=mode,
                            use_word_set=False)

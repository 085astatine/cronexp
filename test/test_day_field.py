# -*- coding: utf-8 -*-

import calendar
import datetime
import math
import unittest
from cronexp._day_field import DayOfMonthField, day_of_month_l, day_of_month_w
from cronexp._field import FieldParseError


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


class DayOfMonthFieldTest(unittest.TestCase):
    def test_normal(self):
        field = DayOfMonthField('*/5', non_standard=False)
        init_date = datetime.date(year=2019, month=1, day=1)
        for total_days in range(0, 365 + 1):
            date = init_date + datetime.timedelta(days=total_days)
            lastday = calendar.monthrange(date.year, date.month)[1]
            next_day = math.ceil(date.day / 5) * 5 + 1
            if next_day > lastday:
                next_day = None
            with self.subTest(year=date.year, month=date.month, day=date.day):
                self.assertEqual(
                        field.next(date.year, date.month, date.day),
                        next_day)

    def test_blank(self):
        field = DayOfMonthField('?', non_standard=True)
        self.assertTrue(field.is_blank)
        date = datetime.date(year=2019, month=1, day=1)
        self.assertEqual(field.next(date.year, date.month, date.day), None)

    def test_l(self):
        field = DayOfMonthField('15,L', non_standard=True)
        init_date = datetime.date(year=2019, month=1, day=1)
        for total_days in range(0, 365 + 1):
            date = init_date + datetime.timedelta(days=total_days)
            lastday = calendar.monthrange(date.year, date.month)[1]
            with self.subTest(year=date.year, month=date.month, day=date.day):
                self.assertEqual(
                        field.next(date.year, date.month, date.day),
                        15 if date.day < 15
                        else lastday if date.day < lastday
                        else None)

    def test_w(self):
        field = DayOfMonthField('10W,20W,30W', non_standard=True)
        init_date = datetime.date(year=2019, month=1, day=1)
        expected_table = [
                [10, 21, 30],  # 2019/01
                [11, 20, 28],  # 2019/02
                [11, 20, 29],  # 2019/03,
                [10, 19, 30],  # 2019/04
                [10, 20, 30],  # 2019/05
                [10, 20, 28],  # 2019/06
                [10, 19, 30],  # 2019/07
                [9, 20, 30],  # 2019/08
                [10, 20, 30],  # 2019/09
                [10, 21, 30],  # 2019/10
                [11, 20, 29],  # 2019/11
                [10, 20, 30]]  # 2019/12
        for total_days in range(0, 365):
            date = init_date + datetime.timedelta(days=total_days)
            expected = None
            for x in expected_table[date.month - 1]:
                if x > date.day:
                    expected = x
                    break
            with self.subTest(year=date.year, month=date.month, day=date.day):
                self.assertEqual(
                    field.next(date.year, date.month, date.day),
                    expected)

    def test_next(self):
        field = DayOfMonthField('*/5,11W,21W,L', non_standard=True)
        init_date = datetime.date(year=2019, month=1, day=1)
        expected_table = [
                [1, 6, 11, 16, 21, 26, 31],  # 2019/01
                [1, 6, 11, 16, 21, 26, 28],  # 2019/02
                [1, 6, 11, 16, 21, 26, 31],  # 2019/03
                [1, 6, 11, 16, 21, 22, 26, 30],  # 2019/04
                [1, 6, 10, 11, 16, 21, 26, 31],  # 2019/05
                [1, 6, 11, 16, 21, 26, 30],  # 2019/06
                [1, 6, 11, 16, 21, 22, 26, 31],  # 2019/07
                [1, 6, 11, 12, 16, 21, 26, 31],  # 2019/08
                [1, 6, 11, 16, 20, 21, 26, 30],  # 2019/09
                [1, 6, 11, 16, 21, 26, 31],  # 2019/10
                [1, 6, 11, 16, 21, 26, 30],  # 2019/11
                [1, 6, 11, 16, 20, 21, 26, 31]]  # 2019/12
        for total_days in range(0, 365):
            date = init_date + datetime.timedelta(days=total_days)
            expected = None
            for x in expected_table[date.month - 1]:
                if x > date.day:
                    expected = x
                    break
            with self.subTest(year=date.year, month=date.month, day=date.day):
                self.assertEqual(
                    field.next(date.year, date.month, date.day),
                    expected)

    def test_error_not_question_only(self):
        field_list = [
                '*,?',
                '?,*',
                '1,?',
                '?,L']
        for field in field_list:
            with self.subTest(field=field):
                with self.assertRaises(FieldParseError):
                    DayOfMonthField(field, non_standard=True)

    def test_error_invalid_w(self):
        field_list = [
                '0W',
                '32W']
        for field in field_list:
            with self.subTest(field=field):
                with self.assertRaises(FieldParseError):
                    DayOfMonthField(field, non_standard=True)

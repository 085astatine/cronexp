# -*- coding: utf-8 -*-

import calendar
import datetime
import math
import unittest
from cronexp._datetime import Dateexp, Timeexp


class TimeexpTest(unittest.TestCase):
    def test_every_minute(self):
        timeexp = Timeexp(minute='*', hour='*')
        for total_minutes in range(0, 24 * 60):
            hour, minute = divmod(total_minutes, 60)
            next_hour, next_minute = divmod(total_minutes + 1, 60)
            move_up = next_hour > 23
            next_hour %= 24
            with self.subTest(hour=hour, minute=minute):
                result = timeexp.next(hour=hour, minute=minute)
                self.assertEqual(result.minute, next_minute)
                self.assertEqual(result.hour, next_hour)
                self.assertEqual(result.move_up, move_up)
                self.assertTrue(timeexp.is_selected(
                        hour=result.hour,
                        minute=result.minute))

    def test_hourly(self):
        timeexp = Timeexp(minute='0', hour='*')
        for total_minutes in range(0, 24 * 60):
            hour, minute = divmod(total_minutes, 60)
            next_hour = (hour + 1) % 24
            move_up = hour >= 23
            with self.subTest(hour=hour, minute=minute):
                result = timeexp.next(hour=hour, minute=minute)
                self.assertEqual(result.minute, 0)
                self.assertEqual(result.hour, next_hour)
                self.assertEqual(result.move_up, move_up)
                self.assertTrue(timeexp.is_selected(
                        hour=result.hour,
                        minute=result.minute))

    def test_daily(self):
        timeexp = Timeexp(minute='45', hour='2')
        for total_minutes in range(0, 24 * 60):
            hour, minute = divmod(total_minutes, 60)
            move_up = total_minutes >= 2 * 60 + 45
            with self.subTest(hour=hour, minute=minute):
                result = timeexp.next(hour=hour, minute=minute)
                self.assertEqual(result.minute, 45)
                self.assertEqual(result.hour, 2)
                self.assertEqual(result.move_up, move_up)
                self.assertTrue(timeexp.is_selected(
                        hour=result.hour,
                        minute=result.minute))

    def test_next(self):
        timeexp = Timeexp(minute='*/10', hour='*/3')
        for total_minutes in range(0, 24 * 60):
            hour, minute = divmod(total_minutes, 60)
            if hour % 3 != 0 or minute >= 50:
                next_hour = math.ceil(hour / 3) * 3
                if hour % 3 == 0 and minute >= 50:
                    next_hour += 3
                next_minute = 0
                move_up = next_hour >= 24
                next_hour %= 24
            else:
                next_hour = hour
                next_minute = math.ceil((minute + 1) / 10) * 10
                move_up = False
            with self.subTest(hour=hour, minute=minute):
                result = timeexp.next(hour=hour, minute=minute)
                self.assertEqual(result.minute, next_minute)
                self.assertEqual(result.hour, next_hour)
                self.assertEqual(result.move_up, move_up)
                self.assertTrue(timeexp.is_selected(
                        hour=result.hour,
                        minute=result.minute))


class DateexpTest(unittest.TestCase):
    def test_every_day(self):
        dateexp = Dateexp(day='*', month='*', weekday='*')
        init_date = datetime.date(year=2019, month=1, day=1)
        for total_days in range(0, 365 + 1):
            date = init_date + datetime.timedelta(days=total_days)
            next_date = date + datetime.timedelta(days=1)
            with self.subTest(year=date.year, month=date.month, day=date.day):
                result = dateexp.next(
                        year=date.year,
                        month=date.month,
                        day=date.day)
                self.assertEqual(result.day, next_date.day)
                self.assertEqual(result.month, next_date.month)
                self.assertEqual(result.year, next_date.year)

    def test_every_month(self):
        dateexp = Dateexp(day='10', month='*', weekday='*')
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
            with self.subTest(year=date.year, month=date.month, day=date.day):
                result = dateexp.next(
                        year=date.year,
                        month=date.month,
                        day=date.day)
                self.assertEqual(result.day, 10)
                self.assertEqual(result.month, next_month)
                self.assertEqual(result.year, next_year)

    def test_yearly(self):
        dateexp = Dateexp(day='2', month='4', weekday='*')
        init_date = datetime.date(year=2019, month=1, day=1)
        for total_days in range(0, 365 + 1):
            date = init_date + datetime.timedelta(days=total_days)
            next_year = date.year
            if date.month > 4 or (date.month == 4 and date.day >= 2):
                next_year += 1
            with self.subTest(year=date.year, month=date.month, day=date.day):
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
            dateexp = Dateexp(day='*', month='*', weekday=weekday)
            init_date = datetime.date(year=2019, month=1, day=1)
            for total_days in range(0, 365 + 1):
                date = init_date + datetime.timedelta(days=total_days)
                delta_day = 7 - (date.weekday() - weekday_index) % 7
                next_date = date + datetime.timedelta(days=delta_day)
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

    def test_next(self):
        dateexp = Dateexp(day='*/10', month='*/3', weekday='*')
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
                if next_day > calendar.monthrange(date.year, date.month)[1]:
                    next_day = 1
                    next_month += 3
                    if next_month > 12:
                        next_month %= 12
                        next_year += 1
            next_date = datetime.date(
                    year=next_year,
                    month=next_month,
                    day=next_day)
            with self.subTest(year=date.year, month=date.month, day=date.day):
                result = dateexp.next(
                        year=date.year,
                        month=date.month,
                        day=date.day)
                self.assertEqual(result.day, next_date.day)
                self.assertEqual(result.month, next_date.month)
                self.assertEqual(result.year, next_date.year)

    def test_day_or_weekday(self):
        dateexp = Dateexp(day='*/5', month='*', weekday='Fri')
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

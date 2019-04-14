# -*- coding: utf-8 -*-

import math
import unittest
from cronexp._datetime import Timeexp


class TimeexpTest(unittest.TestCase):
    def test_every_minute(self):
        timeexp = Timeexp(minute='*', hour='*')
        for total_minutes in range(0, 24 * 60):
            hour, minute = divmod(total_minutes, 60)
            next_hour, next_minute = divmod(total_minutes + 1, 60)
            move_up = next_hour > 23
            next_hour %= 24
            with self.subTest(minute=minute, hour=hour):
                result = timeexp.next(minute, hour)
                self.assertEqual(result.minute, next_minute)
                self.assertEqual(result.hour, next_hour)
                self.assertEqual(result.move_up, move_up)
                self.assertTrue(timeexp.is_selected(
                        minute=result.minute,
                        hour=result.hour))

    def test_hourly(self):
        timeexp = Timeexp(minute='0', hour='*')
        for total_minutes in range(0, 24 * 60):
            hour, minute = divmod(total_minutes, 60)
            next_hour = (hour + 1) % 24
            move_up = hour >= 23
            with self.subTest(minute=minute, hour=hour):
                result = timeexp.next(minute=minute, hour=hour)
                self.assertEqual(result.minute, 0)
                self.assertEqual(result.hour, next_hour)
                self.assertEqual(result.move_up, move_up)
                self.assertTrue(timeexp.is_selected(
                        minute=result.minute,
                        hour=result.hour))

    def test_daily(self):
        timeexp = Timeexp(minute='45', hour='2')
        for total_minutes in range(0, 24 * 60):
            hour, minute = divmod(total_minutes, 60)
            move_up = total_minutes >= 2 * 60 + 45
            with self.subTest(minute=minute, hour=hour):
                result = timeexp.next(minute=minute, hour=hour)
                self.assertEqual(result.minute, 45)
                self.assertEqual(result.hour, 2)
                self.assertEqual(result.move_up, move_up)
                self.assertTrue(timeexp.is_selected(
                        minute=result.minute,
                        hour=result.hour))

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
            with self.subTest(minute=minute, hour=hour):
                result = timeexp.next(minute=minute, hour=hour)
                self.assertEqual(result.minute, next_minute)
                self.assertEqual(result.hour, next_hour)
                self.assertEqual(result.move_up, move_up)
                self.assertTrue(timeexp.is_selected(
                        minute=result.minute,
                        hour=result.hour))

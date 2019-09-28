# -*- coding: utf-8 -*-

import calendar
import datetime
import math
import unittest
from cronexp._cronexp import Cronexp, CronexpOption
from cronexp._dayexp import DaySelectionMode
from cronexp._weekday_field import SundayMode


class CronexpTest(unittest.TestCase):
    def test_cronexp(self):
        cronexp = Cronexp('0 8,19 10/10 * *')
        init = datetime.datetime(2019, 1, 1, 0, 0)
        result_list = [
                datetime.datetime(2019, 1, 10, 8, 0),
                datetime.datetime(2019, 1, 10, 19, 0),
                datetime.datetime(2019, 1, 20, 8, 0),
                datetime.datetime(2019, 1, 20, 19, 0),
                datetime.datetime(2019, 1, 30, 8, 0),
                datetime.datetime(2019, 1, 30, 19, 0),
                datetime.datetime(2019, 2, 10, 8, 0)]
        start = init
        for expect in result_list:
            with self.subTest(start=start):
                self.assertEqual(cronexp.next(start), expect)
                start = expect
        self.assertEqual(
                cronexp.next_list(init, len(result_list)),
                result_list)

    def test_invalid_expression(self):
        expression_list = [
                '*',
                '* *',
                '* * *',
                '* * * *',
                '* * * * * *']
        for expression in expression_list:
            with self.subTest(expression=expression):
                with self.assertRaises(ValueError):
                    cronexp = Cronexp(expression)

    def test_parse_error(self):
        with self.assertRaises(ValueError):
            cronexp = Cronexp(
                    '* * * * Mon',
                    option=CronexpOption(
                            use_word_set=False))
        with self.assertRaises(ValueError):
            cronexp = Cronexp(
                    '* * * * *',
                    option=CronexpOption(
                            day_selection_mode=DaySelectionMode.EITHER))
        with self.assertRaises(ValueError):
            cronexp = Cronexp(
                    '* * * * 0',
                    option=CronexpOption(
                            sunday_mode=SundayMode.SUNDAY_IS_7))

# -*- coding: utf-8 -*-

import itertools
import unittest
from cronexp._field_parser import (
        FieldParser, FieldParseError, month_word_set, weekday_word_set)


class FieldParserStandardTest(unittest.TestCase):
    def test_any(self):
        parser = FieldParser('*', 0, 10)
        result = parser.parse_field()
        self.assertTrue(result.is_any)
        self.assertEqual(result.value, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    def test_single(self):
        parser = FieldParser('5', 0, 10)
        result = parser.parse_field()
        self.assertFalse(result.is_any)
        self.assertEqual(result.value, [5])

    def test_range(self):
        parser = FieldParser('2-6', 0, 10)
        result = parser.parse_field()
        self.assertFalse(result.is_any)
        self.assertEqual(result.value, [2, 3, 4, 5, 6])

    def test_all(self):
        parser = FieldParser('0-10', 0, 10)
        result = parser.parse_field()
        self.assertFalse(result.is_any)
        self.assertEqual(result.value, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    def test_step_all(self):
        parser = FieldParser('*/3', 0, 10)
        result = parser.parse_field()
        self.assertFalse(result.is_any)
        self.assertEqual(result.value, [0, 3, 6, 9])

    def test_step_begin(self):
        parser = FieldParser('1/3', 0, 10)
        result = parser.parse_field()
        self.assertFalse(result.is_any)
        self.assertEqual(result.value, [1, 4, 7, 10])

    def test_step_range(self):
        parser = FieldParser('1-9/3', 0, 10)
        result = parser.parse_field()
        self.assertFalse(result.is_any)
        self.assertEqual(result.value, [1, 4, 7])

    def test_multi(self):
        parser = FieldParser('0,1', 0, 1)
        result = parser.parse_field()
        self.assertFalse(result.is_any)
        self.assertEqual(result.value, [0, 1])

    def test_multi_sort(self):
        parser = FieldParser('1,0', 0, 10)
        result = parser.parse_field()
        self.assertFalse(result.is_any)
        self.assertEqual(result.value, [0, 1])

    def test_multi_uniq(self):
        parser = FieldParser('0,0,0', 0, 10)
        result = parser.parse_field()
        self.assertFalse(result.is_any)
        self.assertEqual(result.value, [0])

    def test_multi_step(self):
        parser = FieldParser('0/3,1/3', 0, 10)
        result = parser.parse_field()
        self.assertFalse(result.is_any)
        self.assertEqual(result.value, [0, 1, 3, 4, 6, 7, 9, 10])

    def test_multi_with_any(self):
        field_list = [
                '0,*',
                '*,0',
                '0-3,*',
                '*,0-3',
                '0/3,*',
                '*,0/3']
        for field in field_list:
            with self.subTest(field=field):
                parser = FieldParser(field, 0, 10)
                result = parser.parse_field()
                self.assertTrue(result.is_any)
                self.assertEqual(
                        result.value,
                        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    def test_error_not_match(self):
        parser = FieldParser('0-1-2', 0, 10)
        with self.assertRaises(FieldParseError):
            parser.parse_field()

    def test_error_out_of_range(self):
        field_list = [
                '0',
                '11',
                '0-10',
                '1-11']
        for field in field_list:
            with self.subTest(field=field):
                parser = FieldParser(field, 1, 10)
                with self.assertRaises(FieldParseError):
                    parser.parse_field()

    def test_error_step0(self):
        parser = FieldParser('*/0', 0, 10)
        with self.assertRaises(FieldParseError):
            parser.parse_field()

    def test_error_invalid_range(self):
        parser = FieldParser('7-3', 0, 10)
        with self.assertRaises(FieldParseError):
            parser.parse_field()


class FieldParserWithWordSet(unittest.TestCase):
    def test_single(self):
        parser = FieldParser('Jan', 1, 12, word_set=month_word_set())
        result = parser.parse_field()
        self.assertFalse(result.is_any)
        self.assertEqual(result.value, [1])

    def test_case_insensitive(self):
        match_list = ['sun', 'Sun', 'SUN']
        mismatch_list = [
                x for x in map(''.join, itertools.product('Ss', 'Uu', 'Nn'))
                if x not in match_list]
        for field in match_list:
            with self.subTest(field=field):
                parser = FieldParser(field, 0, 6, word_set=weekday_word_set())
                result = parser.parse_field()
                self.assertFalse(result.is_any)
                self.assertEqual(result.value, [0])
        for field in mismatch_list:
            with self.subTest(field=field):
                parser = FieldParser(field, 0, 6, word_set=weekday_word_set())
                with self.assertRaises(FieldParseError):
                    parser.parse_field()

    def test_range(self):
        field_list = [
                'Mon-Fri',
                'Mon-5',
                '1-Fri',
                '1-5']
        for field in field_list:
            with self.subTest(field=field):
                parser = FieldParser(field, 0, 6, word_set=weekday_word_set())
                result = parser.parse_field()
                self.assertFalse(result.is_any)
                self.assertEqual(result.value, [1, 2, 3, 4, 5])

    def test_step(self):
        parser = FieldParser('Apr-Dec/2', 1, 12, word_set=month_word_set())
        result = parser.parse_field()
        self.assertFalse(result.is_any)
        self.assertEqual(result.value, [4, 6, 8, 10, 12])

    def test_mixin(self):
        parser = FieldParser('1,Feb', 1, 12, word_set=month_word_set())
        result = parser.parse_field()
        self.assertEqual(result.value, [1, 2])

    def test_error_not_match(self):
        parser = FieldParser('JanFeb', 1, 12, word_set=month_word_set())
        with self.assertRaises(FieldParseError):
            parser.parse_field()

    def test_error_word_in_step(self):
        parser = FieldParser('*/Feb', 1, 12, word_set=month_word_set())
        with self.assertRaises(FieldParseError):
            parser.parse_field()


class FieldParserDayTest(unittest.TestCase):
    def test_standard(self):
        parser = FieldParser('*/10', 1, 31)
        result = parser.parse_day_field()
        self.assertFalse(result.is_any)
        self.assertFalse(result.is_blank)
        self.assertEqual(result.value, [1, 11, 21, 31])
        self.assertFalse(result.last)
        self.assertEqual(result.w, [])

    def test_blank(self):
        parser = FieldParser('?', 1, 31)
        result = parser.parse_day_field()
        self.assertFalse(result.is_any)
        self.assertTrue(result.is_blank)
        self.assertEqual(result.value, [])
        self.assertFalse(result.last)
        self.assertEqual(result.w, [])

    def test_l(self):
        parser = FieldParser('L', 1, 31)
        result = parser.parse_day_field()
        self.assertFalse(result.is_any)
        self.assertFalse(result.is_blank)
        self.assertEqual(result.value, [])
        self.assertTrue(result.last)
        self.assertEqual(result.w, [])

    def test_w(self):
        parser = FieldParser('20W,10W,20W', 1, 31)
        result = parser.parse_day_field()
        self.assertFalse(result.is_any)
        self.assertFalse(result.is_blank)
        self.assertEqual(result.value, [])
        self.assertFalse(result.last)
        self.assertEqual(result.w, [10, 20])

    def test_not_standard(self):
        parser = FieldParser('*/5,L,7W,14W,21W,28W', 1, 31)
        result = parser.parse_day_field()
        self.assertFalse(result.is_any)
        self.assertFalse(result.is_blank)
        self.assertEqual(result.value, [1, 6, 11, 16, 21, 26, 31])
        self.assertTrue(result.last)
        self.assertEqual(result.w, [7, 14, 21, 28])

    def test_w_range(self):
        for w in range(0, 40):
            with self.subTest(w=w):
                parser = FieldParser('{0}W'.format(w), 1, 31)
                if 1 <= w <= 31:
                    result = parser.parse_day_field()
                    self.assertEqual(result.w, [w])
                else:
                    with self.assertRaises(FieldParseError):
                        parser.parse_day_field()

    def test_error_not_question_only(self):
        field_list = [
                '?,*',
                '1,?',
                '?,L,10W']
        for field in field_list:
            with self.subTest(field=field):
                parser = FieldParser(field, 1, 31)
                with self.assertRaises(FieldParseError):
                    parser.parse_day_field()

    def test_error_non_standard(self):
        field_list = [
                '?',
                'L',
                '10W']
        for field in field_list:
            non_standard_parser = FieldParser(field, 1, 31)
            non_standard_parser.parse_day_field(non_standard=True)
            standard_parser = FieldParser(field, 1, 31)
            with self.assertRaises(FieldParseError):
                standard_parser.parse_day_field(non_standard=False)


class FieldParserWeekdayTest(unittest.TestCase):
    def test_standard(self):
        parser = FieldParser('Sun,Sat', 0, 6, word_set=weekday_word_set())
        result = parser.parse_weekday_field()
        self.assertFalse(result.is_any)
        self.assertFalse(result.is_blank)
        self.assertEqual(result.value, [0, 6])
        self.assertEqual(result.last, [])
        self.assertEqual(result.hash, [])

    def test_last(self):
        parser = FieldParser('5L,1L,5L,3L', 0, 6)
        result = parser.parse_weekday_field()
        self.assertFalse(result.is_any)
        self.assertFalse(result.is_blank)
        self.assertEqual(result.value, [])
        self.assertEqual(result.last, [1, 3, 5])
        self.assertEqual(result.hash, [])

    def test_last_with_word_set(self):
        parser = FieldParser(
                'FriL,MONL,friL', 0, 6, word_set=weekday_word_set())
        result = parser.parse_weekday_field()
        self.assertFalse(result.is_any)
        self.assertFalse(result.is_blank)
        self.assertEqual(result.value, [])
        self.assertEqual(result.last, [1, 5])
        self.assertEqual(result.hash, [])

    def test_hash(self):
        parser = FieldParser('0#1,2#3,4#5,6#1,2#3,1#2,3#4', 0, 6)
        result = parser.parse_weekday_field()
        self.assertFalse(result.is_any)
        self.assertFalse(result.is_blank)
        self.assertEqual(result.value, [])
        self.assertEqual(result.last, [])
        self.assertEqual(
                result.hash,
                [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (6, 1)])

    def test_hash_with_word_set(self):
        parser = FieldParser(
                'Sat#4,SAT#2,sat#4', 0, 6, word_set=weekday_word_set())
        result = parser.parse_weekday_field()
        self.assertFalse(result.is_any)
        self.assertFalse(result.is_blank)
        self.assertEqual(result.value, [])
        self.assertEqual(result.last, [])
        self.assertEqual(result.hash, [(6, 2), (6, 4)])

    def test_not_standard(self):
        parser = FieldParser(
                'Mon,Wed,Thu,Tue#2,Tue#4,FriL', 0, 6,
                word_set=weekday_word_set())
        result = parser.parse_weekday_field()
        self.assertFalse(result.is_any)
        self.assertFalse(result.is_blank)
        self.assertEqual(result.value, [1, 3, 4])
        self.assertEqual(result.last, [5])
        self.assertEqual(result.hash, [(2, 2), (2, 4)])

    def test_last_range(self):
        for weekday in range(0, 10):
            with self.subTest(weekday=weekday):
                parser = FieldParser('{0}L'.format(weekday), 0, 6)
                if 0 <= weekday <= 6:
                    result = parser.parse_weekday_field()
                    self.assertFalse(result.is_any)
                    self.assertFalse(result.is_blank)
                    self.assertEqual(result.value, [])
                    self.assertEqual(result.last, [weekday])
                    self.assertEqual(result.hash, [])
                else:
                    with self.assertRaises(FieldParseError):
                        parser.parse_weekday_field()

    def test_hash_range(self):
        for weekday, week_number in itertools.product(
                range(0, 10),
                range(0, 10)):
            with self.subTest(weekday=weekday, week_number=week_number):
                parser = FieldParser(
                        '{0}#{1}'.format(weekday, week_number), 0, 6)
                if 0 <= weekday <= 6 and 1 <= week_number <= 5:
                    result = parser.parse_weekday_field()
                    self.assertFalse(result.is_any)
                    self.assertFalse(result.is_blank)
                    self.assertEqual(result.value, [])
                    self.assertEqual(result.last, [])
                    self.assertEqual(result.hash, [(weekday, week_number)])
                else:
                    with self.assertRaises(FieldParseError):
                        parser.parse_weekday_field()

    def test_error_not_question_only(self):
        field_list = [
                '?,*',
                '1,?',
                '?,SatL,Mon#1']
        for field in field_list:
            with self.subTest(field=field):
                parser = FieldParser(field, 0, 6, word_set=weekday_word_set())
                with self.assertRaises(FieldParseError):
                    parser.parse_weekday_field()

    def test_error_not_use_slash(self):
        parser = FieldParser('*/2', 0, 6)
        with self.assertRaises(FieldParseError):
            parser.parse_weekday_field(use_slash=False)

    def test_error_non_standard(self):
        field_list = [
                '?',
                'FriL',
                'Sat#2']
        for field in field_list:
            non_standard_parser = FieldParser(
                    field, 0, 6, word_set=weekday_word_set())
            non_standard_parser.parse_weekday_field(non_standard=True)
            standard_parser = FieldParser(
                    field, 0, 6, word_set=weekday_word_set())
            with self.assertRaises(FieldParseError):
                standard_parser.parse_weekday_field(non_standard=False)

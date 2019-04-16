# -*- coding: utf-8 -*-

import itertools
import unittest
from cronexp._field import (
        Field, FieldParseError,
        parse_field, month_word_set, weekday_word_set)


class ParseFieldTest(unittest.TestCase):
    def test_any(self):
        self.assertEqual(
                parse_field('*', 0, 10),
                None)

    def test_single(self):
        self.assertEqual(
                parse_field('5', 0, 10),
                [5])

    def test_range(self):
        self.assertEqual(
                parse_field('2-6', 0, 10),
                [2, 3, 4, 5, 6])

    def test_all(self):
        self.assertEqual(
                parse_field('0-10', 0, 10),
                [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    def test_step_all(self):
        self.assertEqual(
                parse_field('*/3', 0, 10),
                [0, 3, 6, 9])

    def test_step_begin(self):
        self.assertEqual(
                parse_field('1/3', 0, 10),
                [1, 4, 7, 10])

    def test_step_range(self):
        self.assertEqual(
                parse_field('1-9/3', 0, 10),
                [1, 4, 7])

    def test_multi(self):
        self.assertEqual(
                parse_field('0,1', 0, 1),
                [0, 1])

    def test_multi_sort(self):
        self.assertEqual(
                parse_field('1,0', 0, 10),
                [0, 1])

    def test_multi_uniq(self):
        self.assertEqual(
                parse_field('0,0,0', 0, 10),
                [0])

    def test_multi_step(self):
        self.assertEqual(
                parse_field('0/3,1/3', 0, 10),
                [0, 1, 3, 4, 6, 7, 9, 10])

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
                self.assertEqual(
                        parse_field(field, 0, 10),
                        None)

    def test_error_not_match(self):
        with self.assertRaises(FieldParseError):
            parse_field('0-1-2', 0, 10)

    def test_error_out_of_range(self):
        field_list = [
                '0',
                '11',
                '0-10',
                '1-11']
        for field in field_list:
            with self.subTest(field=field):
                with self.assertRaises(FieldParseError):
                    parse_field(field, 1, 10)

    def test_error_step0(self):
        with self.assertRaises(FieldParseError):
            parse_field('*/0', 0, 10)

    def test_error_invalid_range(self):
        with self.assertRaises(FieldParseError):
            parse_field('7-3', 0, 10)


class ParseFieldWithWordSet(unittest.TestCase):
    def test_single(self):
        self.assertEqual(
                parse_field('Jan', 1, 12, word_set=month_word_set()),
                [1])

    def test_case_insensitive(self):
        for product in itertools.product('Ss', 'Uu', 'Nn'):
            field = ''.join(product)
            with self.subTest(field=field):
                self.assertEqual(
                    parse_field(field, 0, 6, word_set=weekday_word_set()),
                    [0])

    def test_range(self):
        field_list = [
                'Mon-Fri',
                'Mon-5',
                '1-Fri',
                '1-5']
        for field in field_list:
            with self.subTest(field=field):
                self.assertEqual(
                        parse_field(field, 0, 6, word_set=weekday_word_set()),
                        [1, 2, 3, 4, 5])

    def test_step(self):
        self.assertEqual(
                parse_field('Apr-Dec/2', 1, 12, word_set=month_word_set()),
                [4, 6, 8, 10, 12])

    def test_mixin(self):
        self.assertEqual(
                parse_field('1,Feb', 1, 12, word_set=month_word_set()),
                [1, 2])

    def test_error_not_match(self):
        with self.assertRaises(FieldParseError):
            parse_field('JanFeb', 1, 12, word_set=month_word_set())

    def test_error_word_in_step(self):
        with self.assertRaises(FieldParseError):
            parse_field('*/Feb', 1, 12, word_set=month_word_set())


class FieldTest(unittest.TestCase):
    def test_field(self):
        selected = [2, 3, 5, 7]
        field = Field('2,3,5,7', 0, 10)
        self.assertFalse(field.is_any)
        for i in range(0, 12):
            with self.subTest(i=i):
                self.assertEqual(field.is_selected(i), i in selected)

    def test_any_field(self):
        field = Field('*', 0, 10)
        self.assertTrue(field.is_any)
        for i in range(0, 12):
            with self.subTest(i=i):
                self.assertEqual(field.is_selected(i), 0 <= i <= 10)

    def test_next(self):
        field = Field('5,8', 0, 10)
        for i in range(0, 11):
            with self.subTest(i=i):
                result = field.next(i)
                if i < 5:
                    self.assertEqual(result.value, 5)
                    self.assertFalse(result.move_up)
                elif 5 <= i < 8:
                    self.assertEqual(result.value, 8)
                    self.assertFalse(result.move_up)
                else:
                    self.assertEqual(result.value, 5)
                    self.assertTrue(result.move_up)

    def test_next_greater_than_max(self):
        field = Field('1', 0, 10)
        result = field.next(11)
        self.assertEqual(result.value, 1)
        self.assertTrue(result.move_up)

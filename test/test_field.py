# -*- coding: utf-8 -*-

import unittest
from cronexp._field import FieldParseError, parse_field


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

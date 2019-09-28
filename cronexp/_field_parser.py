# -*- coding: utf-8 -*-

import re
from typing import Dict, List, NamedTuple, Optional, Tuple


class FieldElementParseError(NamedTuple):
    expression: str
    reason: str


class FieldParseError(Exception):
    def __init__(
            self,
            field: str,
            mismatched: List[str],
            parse_error: List[FieldElementParseError]) -> None:
        super().__init__()
        self.field = field
        self.mismatched = mismatched
        self.parse_error = parse_error

    def __str__(self) -> str:
        line: List[str] = []
        line.append('Failed to parse "{0}"'.format(self.field))
        line.extend('  "{0}": unkown pattern'.format(mismatched)
                    for mismatched in self.mismatched)
        line.extend('  "{0}": {1}'.format(error.expression, error.reason)
                    for error in self.parse_error)
        return '{0}\n'.format('\n'.join(line))


class FieldParseResult(NamedTuple):
    source: str
    is_any: bool
    value: List[int]


class DayFieldParseResult(NamedTuple):
    source: str
    is_any: bool
    is_blank: bool
    value: List[int]
    last: bool
    w: List[int]


class WeekdayFieldParseResult(NamedTuple):
    source: str
    is_any: bool
    is_blank: bool
    value: List[int]
    last: List[int]
    hash: List[Tuple[int, int]]


class FieldParser:
    def __init__(
            self,
            field: str,
            min_: int,
            max_: int,
            word_set: Optional[Dict[str, int]] = None) -> None:
        self._origin = field
        self._min = min_
        self._max = max_
        self._word_set = word_set
        # parse result
        self._is_any = False
        self._is_blank = False
        self._value: List[int] = []
        self._day_last = False
        self._day_w: List[int] = []
        self._weekday_last: List[int] = []
        self._weekday_hash: List[Tuple[int, int]] = []
        # parse error
        self._element_list = field.split(',')
        self._parse_error: List[FieldElementParseError] = []

    def parse_field(self) -> FieldParseResult:
        self._parse_standard()
        self._error_check()
        return FieldParseResult(
                source=self._origin,
                is_any=self._is_any,
                value=self._value)

    def parse_day_field(
            self,
            non_standard: bool = True) -> DayFieldParseResult:
        self._parse_standard()
        if non_standard:
            self._parse_question()
            self._parse_day()
        self._error_check()
        return DayFieldParseResult(
                source=self._origin,
                is_any=self._is_any,
                is_blank=self._is_blank,
                value=self._value,
                last=self._day_last,
                w=self._day_w)

    def parse_weekday_field(
            self,
            non_standard: bool = True,
            use_slash: bool = True) -> WeekdayFieldParseResult:
        self._parse_standard(use_slash=use_slash)
        if non_standard:
            self._parse_question()
            self._parse_weekday()
        self._error_check()
        return WeekdayFieldParseResult(
                source=self._origin,
                is_any=self._is_any,
                is_blank=self._is_blank,
                value=self._value,
                last=self._weekday_last,
                hash=self._weekday_hash)

    def _parse_standard(self, use_slash: bool = True) -> None:
        pattern = re.compile(
                r'^(\*|(?P<begin>{0})(|-(?P<end>{0})))'
                r'(|/(?P<step>[0-9]+))$'
                .format(_word_set_to_regex(self._word_set)))
        for element in self._element_list[:]:
            match = pattern.match(element)
            if match is None:
                continue
            self._element_list.remove(element)
            # parameter
            begin = _read_word(match.group('begin'), self._word_set)
            end = _read_word(match.group('end'), self._word_set)
            step = (int(match.group('step'))
                    if match.group('step') is not None else None)
            # error check
            if begin is not None and not self._min <= begin <= self._max:
                self._add_error(
                        element,
                        '{0} is out of range({1}...{2})'
                        .format(begin, self._min, self._max))
                continue
            if end is not None and not self._min <= end <= self._max:
                self._add_error(
                        element,
                        '{0} is out of range({1}...{2})'
                        .format(end, self._min, self._max))
                continue
            if step is not None and step <= 0:
                self._add_error(element, 'step must be positive value')
                continue
            if begin is not None and end is not None and end < begin:
                self._add_error(
                        element,
                        'invalid range({0}...{1})'.format(begin, end))
                continue
            if not use_slash and step is not None:
                self._add_error(element, '"/" is not allowed')
                continue
            # evaluate
            evaluated = _evaluate_standard(
                    self._min,
                    self._max,
                    begin,
                    end,
                    step)
            if evaluated is None:
                self._is_any = True
                self._value.extend(range(self._min, self._max + 1))
            else:
                self._value.extend(evaluated)
        self._value = sorted(set(self._value))

    def _parse_question(self) -> None:
        for element in self._element_list[:]:
            if element != '?':
                continue
            self._element_list.remove(element)
            self._is_blank = True
            if self._origin != '?':
                self._add_error(element, 'there is a charactor other than "?"')

    def _parse_day(self) -> None:
        # L
        for element in self._element_list[:]:
            if element != 'L':
                continue
            self._element_list.remove(element)
            self._day_last = True
        # <N>W
        w_pattern = re.compile(r'^(?P<target>[0-9]+)W$')
        for element in self._element_list[:]:
            match = w_pattern.match(element)
            if match is None:
                continue
            self._element_list.remove(element)
            w_target = int(match.group('target'))
            if self._min <= w_target <= self._max:
                self._day_w.append(w_target)
            else:
                self._add_error(
                        element,
                        '{0} is out of range({1}...{2})'
                        .format(w_target, self._min, self._max))
        self._day_w = sorted(set(self._day_w))

    def _parse_weekday(self) -> None:
        # <N>L
        l_pattern = re.compile(
                r'^(?P<weekday>{0})L$'
                .format(_word_set_to_regex(self._word_set)))
        for element in self._element_list[:]:
            match = l_pattern.match(element)
            if not match:
                continue
            self._element_list.remove(element)
            weekday = _read_word(match.group('weekday'), self._word_set)
            if weekday is not None and self._min <= weekday <= self._max:
                self._weekday_last.append(weekday)
            else:
                self._add_error(
                        element,
                        '{0} is out of range({1}...{2})'
                        .format(weekday, self._min, self._max))
        self._weekday_last = sorted(set(self._weekday_last))
        # <N>#<N>
        hash_pattern = re.compile(
                r'^(?P<weekday>{0})#(?P<week_number>[0-9]+)$'
                .format(_word_set_to_regex(self._word_set)))
        for element in self._element_list[:]:
            match = hash_pattern.match(element)
            if not match:
                continue
            self._element_list.remove(element)
            weekday = _read_word(match.group('weekday'), self._word_set)
            week_number = int(match.group('week_number'))
            if weekday is None or not self._min <= weekday <= self._max:
                self._add_error(
                        element,
                        '{0} is out of range({1}...{2})'
                        .format(weekday, self._min, self._max))
            elif not 1 <= week_number <= 5:
                self._add_error(
                        element,
                        '{0} is out of range({1}...{2})'
                        .format(week_number, 1, 5))
            else:
                self._weekday_hash.append((weekday, week_number))
        self._weekday_hash = sorted(set(self._weekday_hash))

    def _add_error(
            self,
            element: str,
            reason: str) -> None:
        self._parse_error.append(FieldElementParseError(element, reason))

    def _error_check(self) -> None:
        if self._element_list or self._parse_error:
            raise FieldParseError(
                    field=self._origin,
                    mismatched=self._element_list,
                    parse_error=self._parse_error)


def month_word_set() -> Dict[str, int]:
    return {'jan': 1,
            'feb': 2,
            'mar': 3,
            'apr': 4,
            'may': 5,
            'jun': 6,
            'jul': 7,
            'aug': 8,
            'sep': 9,
            'oct': 10,
            'nov': 11,
            'dec': 12}


def weekday_word_set() -> Dict[str, int]:
    return {'sun': 0,
            'mon': 1,
            'tue': 2,
            'wed': 3,
            'thu': 4,
            'fri': 5,
            'sat': 6}


def _evaluate_standard(
        min_: int,
        max_: int,
        begin: Optional[int],
        end: Optional[int],
        step: Optional[int]) -> Optional[List[int]]:
    if step is None:
        if begin is None:
            return None
        if end is None:
            return [begin]
        return list(range(begin, end + 1))
    result: List[int] = []
    init = begin if begin is not None else min_
    last = end if end is not None else max_
    if init < last and step > 0:
        value = init
        while value <= last:
            result.append(value)
            value += step
    return result


def _word_set_to_regex(word_set: Optional[Dict[str, int]]) -> str:
    return (r'({0}|[0-9]+)'.format(
                '|'.join(f'{x.lower()}|{x.upper()}|{x.title()}'
                         for x in word_set.keys()))
            if word_set else r'[0-9]+')


def _read_word(
        word: Optional[str],
        word_set: Optional[Dict[str, int]]) -> Optional[int]:
    if word is not None:
        if word.isdigit():
            return int(word)
        if word_set:
            return word_set[word.lower()]
    return None

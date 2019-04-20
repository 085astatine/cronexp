# -*- coding: utf-8 -*-

import re
from typing import Dict, List, NamedTuple, Optional


class FieldElementParseError(NamedTuple):
    expression: str
    reason: str


class FieldParseError(Exception):
    def __init__(
            self,
            field: str,
            mismatched: List[str],
            parse_error: List[FieldElementParseError]) -> None:
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
    selected: List[int]
    mismatched: List[str]
    error: List[FieldElementParseError]


class FieldNext(NamedTuple):
    value: int
    move_up: bool


class Field:
    def __init__(
            self,
            field: str,
            min_: int,
            max_: int,
            word_set: Optional[Dict[str, int]] = None) -> None:
        result = parse_field(field, min_, max_, word_set)
        self._is_any = result.is_any
        self._selected_list = result.selected
        if result.mismatched or result.error:
            raise FieldParseError(
                    result.source,
                    result.mismatched,
                    result.error)

    @property
    def is_any(self) -> bool:
        return self._is_any

    def next(self, value: int) -> FieldNext:
        for i in self._selected_list:
            if value < i:
                return FieldNext(value=i, move_up=False)
        else:
            return FieldNext(value=self.min(), move_up=True)

    def is_selected(self, value: int) -> bool:
        return value in self._selected_list

    def min(self) -> int:
        return min(self._selected_list)

    def max(self) -> int:
        return max(self._selected_list)


def evaluate_field(
        min_: int,
        max_: int,
        begin: Optional[int],
        end: Optional[int],
        step: Optional[int]) -> Optional[List[int]]:
    if step is None:
        if begin is None:
            return None
        else:
            if end is None:
                return [begin]
            else:
                return list(range(begin, end + 1))
    else:
        result: List[int] = []
        init = begin if begin is not None else min_
        last = end if end is not None else max_
        if init < last and 0 < step:
            value = init
            while value <= last:
                result.append(value)
                value += step
        return result


def parse_field(
        field: str,
        min_: int,
        max_: int,
        word_set: Optional[Dict[str, int]] = None) -> FieldParseResult:
    is_any = False
    selected: List[int] = []
    mismatched: List[str] = []
    error: List[FieldElementParseError] = []
    for element in field.split(','):
        begin: Optional[int] = None
        end: Optional[int] = None
        step: Optional[int] = None
        match = re.match(
                r'^(\*|(?P<begin>[0-9]+)(|-(?P<end>[0-9]+)))'
                r'(|/(?P<step>[0-9]+))$',
                element)
        if match:
            begin = (int(match.group('begin'))
                     if match.group('begin') is not None else None)
            end = (int(match.group('end'))
                   if match.group('end') is not None else None)
            step = (int(match.group('step'))
                    if match.group('step') is not None else None)
        elif word_set:
            match = re.match(
                    r'^(?P<begin>({0}|[0-9]+))(|-(?P<end>({0}|[0-9]+)))'
                    r'(|/(?P<step>[0-9]+))$'
                    .format('|'.join(word_set.keys())),
                    element,
                    re.IGNORECASE)
            if match:
                begin = (int(word_set.get(
                                match.group('begin').lower(),
                                match.group('begin')))
                         if match.group('begin') is not None else None)
                end = (int(word_set.get(
                                match.group('end').lower(),
                                match.group('end')))
                       if match.group('end') is not None else None)
                step = (int(match.group('step'))
                        if match.group('step') is not None else None)
        # mismatched
        if match is None:
            mismatched.append(element)
            continue
        # error check
        if begin is not None and not min_ <= begin <= max_:
            error.append(FieldElementParseError(
                    element,
                    '{0} is out of range({1}...{2})'
                    .format(begin, min_, max_)))
            continue
        if end is not None and not min_ <= end <= max_:
            error.append(FieldElementParseError(
                    element,
                    '{0} is out of range({1}...{2})'
                    .format(end, min_, max_)))
            continue
        if step is not None and step <= 0:
            error.append(FieldElementParseError(
                    element,
                    'step must be positive value'))
            continue
        if begin is not None and end is not None and end < begin:
            error.append(FieldElementParseError(
                    element,
                    'invalid range({0}...{1})'.format(begin, end)))
            continue
        # evaluate
        evaluated = evaluate_field(min_, max_, begin, end, step)
        if evaluated is None:
            is_any = True
            selected.extend(range(min_, max_ + 1))
        else:
            selected.extend(evaluated)
    return FieldParseResult(
            source=field,
            is_any=is_any,
            selected=sorted(set(selected)),
            mismatched=mismatched,
            error=error)


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

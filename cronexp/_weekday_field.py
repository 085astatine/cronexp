# -*- coding: utf-8 -*-

import calendar
import re
from typing import List, Optional, Tuple
from ._field import (
        FieldBase, FieldParseError, FieldElementParseError,
        parse_field, weekday_word_set, word_set_to_regex, read_word)


class DayOfWeekField(FieldBase):
    def __init__(self, field: str, non_standard: bool) -> None:
        # initialize base
        min_ = 0
        max_ = 6
        word_set = weekday_word_set()
        result = parse_field(field, min_, max_, word_set=word_set)
        super().__init__(result)
        # additional variables
        self._non_standard = non_standard
        self._is_blank = False
        self._l: List[int] = []
        self._sharp: List[Tuple[int, int]] = []
        # parse not standard
        mismatched = result.mismatched
        error = result.error
        if self._non_standard:
            mismatched = []
            for element in result.mismatched:
                l_match = re.match(
                        r'^(?P<weekday>{0})L$'
                        .format(word_set_to_regex(word_set)),
                        element)
                sharp_match = re.match(
                        r'^(?P<weekday>{0})#(?P<week_number>[0-9]+)$'
                        .format(word_set_to_regex(word_set)),
                        element)
                if element == '?':
                    self._is_blank = True
                    if field != '?':
                        error.append(FieldElementParseError(
                                element,
                                'there is a charactor other than "?"'))
                elif l_match:
                    weekday = read_word(l_match.group('weekday'), word_set)
                    if weekday is not None and min_ <= weekday <= max_:
                        self._l.append(weekday)
                    else:
                        error.append(FieldElementParseError(
                                element,
                                '{0} is out of range({1}...{2})'
                                .format(weekday, min_, max_)))
                elif sharp_match:
                    weekday = read_word(sharp_match.group('weekday'), word_set)
                    week_number = int(sharp_match.group('week_number'))
                    if weekday is None or not min_ <= weekday <= max_:
                        error.append(FieldElementParseError(
                                element,
                                '{0} is out of range({1}...{2})'
                                .format(weekday, min_, max_)))
                    elif not 1 <= week_number <= 5:
                        error.append(FieldElementParseError(
                                element,
                                '{0} is out of range({1}...{2})'
                                .format(week_number, 1, 5)))
                    else:
                        self._sharp.append((weekday, week_number))
                else:
                    mismatched.append(element)
        # error check
        if mismatched or error:
            raise FieldParseError(
                    field=field,
                    mismatched=mismatched,
                    parse_error=error)

    @property
    def is_blank(self) -> bool:
        return self._is_blank

    def next(self, year: int, month: int, day: Optional[int]) -> Optional[int]:
        init_weekday, lastday = calendar.monthrange(year, month)
        # 0: Mon,... 6:Sun -> 0: Sun, ..., 6: Sat
        init_weekday = (init_weekday + 1) % 7

        def next_day(day_: Optional[int]) -> Optional[int]:
            if day_ is None:
                if self.is_selected(init_weekday):
                    return 1
                day_ = 1
                weekday = init_weekday
            elif lastday < day_:
                return None
            else:
                weekday = (init_weekday + day_ - 1) % 7
            next_weekday = self.next_value(weekday)
            if next_weekday is None:
                next_weekday = self.next_value(None)
                if next_weekday is None:
                    return None
            day_ += 7 - (weekday - next_weekday) % 7
            return day_ if day_ <= lastday else None

        target: List[Optional[int]] = [next_day(day)]
        if self._non_standard:
            if self._is_blank:
                return None
            target.extend(day_of_week_l(l, year, month, day) for l in self._l)
            target.extend(
                    day_of_week_sharp(weekday, week_number, year, month, day)
                    for weekday, week_number in self._sharp)
        return min(
                filter(lambda x: x is not None and x <= lastday, target),
                default=None)


def day_of_week_l(
        weekday: int,
        year: int,
        month: int,
        day: Optional[int]) -> Optional[int]:
    # weekday 0: Sunday, ... 6: Saturday
    # init_weekday: 0: Monday, ... 6: Sunday
    init_weekday, lastday = calendar.monthrange(year, month)
    result = lastday - (init_weekday + lastday - weekday) % 7
    return result if day is None or day < result else None


def day_of_week_sharp(
        weekday: int,
        week_number: int,
        year: int,
        month: int,
        day: Optional[int]) -> Optional[int]:
    # weekday 0: Sunday, ... 6: Saturday
    # init_weekday: 0: Monday, ... 6: Sunday
    init_weekday, lastday = calendar.monthrange(year, month)
    result = 1 + (weekday - init_weekday - 1) % 7 + 7 * (week_number - 1)
    if result <= lastday:
        return result if day is None or day < result else None
    return None

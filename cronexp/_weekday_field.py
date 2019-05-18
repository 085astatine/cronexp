# -*- coding: utf-8 -*-

import calendar
from typing import List, Optional
from ._field_parser import FieldParser, weekday_word_set


class DayOfWeekField:
    def __init__(
            self,
            field: str,
            use_word_set: bool,
            non_standard: bool) -> None:
        self._non_standard = non_standard
        min_ = 0
        max_ = 6
        word_set = weekday_word_set() if use_word_set else None
        parser = FieldParser(field, min_, max_, word_set=word_set)
        result = parser.parse_weekday_field(
                non_standard=non_standard,
                use_slash=True)
        self._is_any = result.is_any
        self._is_blank = result.is_blank
        self._value = result.value
        self._l = result.last
        self._hash = result.hash

    @property
    def is_any(self) -> bool:
        return self._is_any

    @property
    def is_blank(self) -> bool:
        return self._is_blank

    def next(self, year: int, month: int, day: Optional[int]) -> Optional[int]:
        init_weekday, lastday = calendar.monthrange(year, month)
        # 0: Mon,... 6:Sun -> 0: Sun, ..., 6: Sat
        init_weekday = (init_weekday + 1) % 7

        def next_day(day_: Optional[int]) -> Optional[int]:
            if day_ is None:
                if init_weekday in self._value:
                    return 1
                day_ = 1
                weekday = init_weekday
            elif lastday < day_:
                return None
            else:
                weekday = (init_weekday + day_ - 1) % 7
            next_weekday = min(
                    filter(lambda x: x is None or x > weekday, self._value),
                    default=None)
            if next_weekday is None:
                next_weekday = min(self._value, default=None)
                if next_weekday is None:
                    return None
            day_ += 7 - (weekday - next_weekday) % 7
            return day_ if day_ <= lastday else None

        target: List[Optional[int]] = [next_day(day)]
        if self._non_standard:
            if self._is_blank:
                return None
            target.extend(day_of_week_l(l, year, month) for l in self._l)
            target.extend(
                    day_of_week_hash(weekday, week_number, year, month)
                    for weekday, week_number in self._hash)
        return min(
                filter(lambda x: x is not None and (day is None or day < x),
                       target),
                default=None)

    def is_selected(self, year: int, month: int, day: int) -> bool:
        if self._non_standard and self._is_blank:
            return False
        lastday = calendar.monthrange(year, month)[1]
        if 1 <= day <= lastday:
            weekday = (calendar.weekday(year, month, day) + 1) % 7
            if weekday in self._value:
                return True
            if self._non_standard:
                if day in [day_of_week_l(weekday, year, month)
                           for weekday in self._l]:
                    return True
                if day in [day_of_week_hash(weekday, week_number, year, month)
                           for weekday, week_number in self._hash]:
                    return True
        return False


def day_of_week_l(
        weekday: int,
        year: int,
        month: int) -> int:
    # weekday 0: Sunday, ... 6: Saturday
    # init_weekday: 0: Monday, ... 6: Sunday
    init_weekday, lastday = calendar.monthrange(year, month)
    return lastday - (init_weekday + lastday - weekday) % 7


def day_of_week_hash(
        weekday: int,
        week_number: int,
        year: int,
        month: int) -> Optional[int]:
    # weekday 0: Sunday, ... 6: Saturday
    # init_weekday: 0: Monday, ... 6: Sunday
    init_weekday, lastday = calendar.monthrange(year, month)
    result = 1 + (weekday - init_weekday - 1) % 7 + 7 * (week_number - 1)
    return result if result <= lastday else None

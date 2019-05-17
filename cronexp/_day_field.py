# -*- coding: utf-8 -*-

import calendar
from typing import List, Optional
from ._field_parser import FieldParser


class DayOfMonthField:
    def __init__(self, field: str, non_standard: bool) -> None:
        self._non_standard = non_standard
        parser = FieldParser(field, 1, 31)
        result = parser.parse_day_field(non_standard=non_standard)
        self._is_any = result.is_any
        self._is_blank = result.is_blank
        self._value = result.value
        self._l = result.last
        self._w = result.w

    @property
    def is_any(self) -> bool:
        return self._is_any

    @property
    def is_blank(self) -> bool:
        return self._is_blank

    def next(self, year: int, month: int, day: Optional[int]) -> Optional[int]:
        lastday = calendar.monthrange(year, month)[1]
        target: List[Optional[int]] = []
        target.extend(self._value)
        if self._non_standard:
            if self.is_blank:
                return None
            if self._l:
                target.append(lastday)
            target.extend(day_of_month_w(w, year, month) for w in self._w)
        return min(
                filter(lambda x: (
                            x is not None
                            and x <= lastday
                            and (day is None or day < x)),
                       target),
                default=None)


def day_of_month_w(
        target: int,
        year: int,
        month: int) -> int:
    lastday = calendar.monthrange(year, month)[1]
    result = min(target, lastday)
    weekday = calendar.weekday(year, month, result)
    if weekday > 4:
        if result == 1:
            result += 2 if weekday == 5 else 1
        elif result == lastday:
            result += -1 if weekday == 5 else -2
        else:
            result += -1 if weekday == 5 else 1
    return result

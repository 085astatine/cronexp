# -*- coding: utf-8 -*-

import calendar
import re
from typing import List, Optional
from ._field import (
        FieldBase, FieldParseError, FieldElementParseError, parse_field)


class DayOfMonthField(FieldBase):
    def __init__(self, field: str, non_standard: bool) -> None:
        # initialize base
        min_ = 1
        max_ = 31
        result = parse_field(field, min_, max_)
        super().__init__(result)
        # additional variables
        self._non_standard = non_standard
        self._is_blank = False
        self._l = False
        self._w: List[int] = []
        # parse not standard
        mismatched = result.mismatched
        error = result.error
        if self._non_standard:
            mismatched = []
            for element in result.mismatched:
                w_match = re.match('^(?P<target>[0-9]+)W$', element)
                if element == '?':
                    self._is_blank = True
                    if field != '?':
                        error.append(FieldElementParseError(
                                element,
                                'there is a charactor other than "?"'))
                elif element == 'L':
                    self._l = True
                elif w_match:
                    w_target = int(w_match.group('target'))
                    if min_ <= w_target <= max_:
                        self._w.append(w_target)
                    else:
                        error.append(FieldElementParseError(
                                element,
                                '{0} is out of range({1}...{2})'
                                .format(w_target, min_, max_)))
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

    def next(self, year: int, month: int, day: int) -> Optional[int]:
        lastday = calendar.monthrange(year, month)[1]
        if self._non_standard:
            if self.is_blank:
                return None
            target: List[Optional[int]] = []
            target.append(self.next_value(day))
            if self._l:
                target.append(day_of_month_l(year, month, day))
            target.extend(day_of_month_w(w, year, month, day) for w in self._w)
            return min(
                    (x for x in target if x is not None and x <= lastday),
                    default=None)
        else:
            result = self.next_value(day)
            return result if result is not None and result <= lastday else None


def day_of_month_l(year: int, month: int, day: int) -> Optional[int]:
    lastday = calendar.monthrange(year, month)[1]
    return lastday if lastday > day else None


def day_of_month_w(
        target: int,
        year: int,
        month: int,
        day: int) -> Optional[int]:
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
    return result if result > day else None

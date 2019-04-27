# -*- coding: utf-8 -*-

import calendar
from typing import List, Optional


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

# -*- coding: utf-8 -*-

import calendar
from typing import List, Optional


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

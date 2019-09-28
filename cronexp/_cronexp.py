# -*- coding: utf-8 -*-

import datetime
from typing import List, NamedTuple, Optional
from ._dateexp import Dateexp, DateexpNext
from ._dayexp import DayexpParseError, DaySelectionMode
from ._field_parser import FieldParseError
from ._timeexp import Timeexp
from ._weekday_field import SundayMode


class CronexpOption(NamedTuple):
    max_year: Optional[int] = None
    use_word_set: bool = True
    day_selection_mode: DaySelectionMode = DaySelectionMode.OR
    sunday_mode: SundayMode = SundayMode.SUNDAY_IS_0


class Cronexp:
    def __init__(
            self,
            expression: str,
            option: CronexpOption = CronexpOption()) -> None:
        field_list = expression.split()
        if len(field_list) != 5:
            raise ValueError(
                    'expression("{0}") has {1} fields. '
                    'expression must have 5 fields.'
                    .format(expression, len(field_list)))
        try:
            self._timeexp = Timeexp(
                    minute=field_list[0],
                    hour=field_list[1])
            self._dateexp = Dateexp(
                    day=field_list[2],
                    month=field_list[3],
                    weekday=field_list[4],
                    day_selection_mode=option.day_selection_mode,
                    max_year=option.max_year,
                    use_word_set=option.use_word_set,
                    sunday_mode=option.sunday_mode)
        except (DayexpParseError, FieldParseError) as parse_error:
            raise ValueError(str(parse_error))

    def next(
            self,
            start: datetime.datetime) -> Optional[datetime.datetime]:
        next_time = self._timeexp.next(
                minute=start.minute,
                hour=start.hour)
        next_date: Optional[DateexpNext] = None
        if (not next_time.move_up
                and self._dateexp.is_selected(
                        year=start.year,
                        month=start.month,
                        day=start.day)):
            next_date = DateexpNext(
                    day=start.day,
                    month=start.month,
                    year=start.year)
        else:
            next_date = self._dateexp.next(
                    year=start.year,
                    month=start.month,
                    day=start.day + (1 if next_time.move_up else 0))
        if next_date is not None:
            return datetime.datetime(
                    year=next_date.year,
                    month=next_date.month,
                    day=next_date.day,
                    hour=next_time.hour,
                    minute=next_time.minute,
                    tzinfo=start.tzinfo)
        return None

    def next_list(
            self,
            start: datetime.datetime,
            length: int) -> List[datetime.datetime]:
        result: List[datetime.datetime] = []
        while len(result) < length:
            next_ = self.next(result[-1] if result else start)
            if next_ is not None:
                result.append(next_)
            else:
                break
        return result

# -*- coding: utf-8 -*-

from typing import NamedTuple, Optional
from ._dayexp import Dayexp, DaySelectionMode
from ._field import Field
from ._field_parser import month_word_set
from ._weekday_field import SundayMode


class DateexpNext(NamedTuple):
    day: int
    month: int
    year: int


class Dateexp:
    def __init__(
            self,
            day: str,
            month: str,
            weekday: str,
            day_selection_mode: DaySelectionMode,
            max_year: Optional[int] = None,
            use_word_set: bool = True,
            sunday_mode: SundayMode = SundayMode.SUNDAY_IS_0) -> None:
        self._dayexp = Dayexp(
                day,
                weekday,
                selection_mode=day_selection_mode,
                use_word_set=use_word_set,
                sunday_mode=sunday_mode)
        self._month = Field(
                month, 1, 12,
                word_set=month_word_set() if use_word_set else None)
        self._max_year = max_year

    def next(self, day: int, month: int, year: int) -> Optional[DateexpNext]:
        def impl(
                year_: int,
                month_: int,
                day_: Optional[int]) -> Optional[DateexpNext]:
            if not self._month.is_selected(month_):
                next_month = self._month.next(month_)
                day_ = None
                month_ = next_month.value
                if next_month.move_up:
                    year_ += 1
            day_ = self._dayexp.next(year_, month_, day_)
            if day_ is not None:
                return DateexpNext(year=year_, month=month_, day=day_)
            next_month = self._month.next(month_)
            month_ = next_month.value
            if next_month.move_up:
                year_ += 1
                if self._max_year is not None and self._max_year < year_:
                    return None
            return impl(year_, month_, day_)

        return impl(year, month, day)

    def is_selected(self, year: int, month: int, day: int) -> bool:
        return (self._month.is_selected(month)
                and self._dayexp.is_selected(year, month, day))

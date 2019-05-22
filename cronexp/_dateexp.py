# -*- coding: utf-8 -*-

from typing import NamedTuple, Optional
from ._dayexp import Dayexp, DaySelectionMode
from ._field import Field
from ._field_parser import month_word_set


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
            day_selection_mode: DaySelectionMode) -> None:
        self._dayexp = Dayexp(day, weekday, selection_mode=day_selection_mode)
        self._month = Field(month, 1, 12, word_set=month_word_set())

    def next(self, day: int, month: int, year: int) -> DateexpNext:
        def impl(
                year_: int,
                month_: int,
                day_: Optional[int]) -> DateexpNext:
            if not self._month.is_selected(month_):
                next_month = self._month.next(month_)
                day_ = None
                month_ = next_month.value
                if next_month.move_up:
                    year_ += 1
            day_ = self._dayexp.next(year_, month_, day_)
            if day_ is not None:
                return DateexpNext(year=year_, month=month_, day=day_)
            else:
                next_month = self._month.next(month_)
                month_ = next_month.value
                if next_month.move_up:
                    year_ += 1
                return impl(year_, month_, day_)

        return impl(year, month, day)

    def is_selected(self, year: int, month: int, day: int) -> bool:
        return (self._month.is_selected(month)
                and self._dayexp.is_selected(year, month, day))

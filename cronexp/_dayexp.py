# -*- coding: utf-8 -*-

import enum
from typing import Optional
from ._day_field import DayOfMonthField
from ._weekday_field import DayOfWeekField


class DaySelectionMode(enum.Enum):
    OR = enum.auto()
    AND = enum.auto()
    EITHER = enum.auto()


class Dayexp:
    def __init__(
            self,
            day: str,
            weekday: str,
            selection_mode: DaySelectionMode) -> None:
        self._mode = selection_mode
        self._day_of_month = DayOfMonthField(
                day,
                non_standard=self._mode is DaySelectionMode.EITHER)
        self._day_of_week = DayOfWeekField(
                weekday,
                use_word_set=True,
                non_standard=self._mode is DaySelectionMode.EITHER)
        if (self._mode is DaySelectionMode.EITHER
                and self._day_of_month.is_blank == self._day_of_week.is_blank):
            raise ValueError()

    def next(self, year: int, month: int, day: Optional[int]) -> Optional[int]:
        next_day_of_month = self._day_of_month.next(year, month, day)
        next_day_of_week = self._day_of_week.next(year, month, day)
        if self._mode is DaySelectionMode.OR:
            if not self._day_of_month.is_any and not self._day_of_week.is_any:
                return min(filter(lambda x: x is not None,
                                  [next_day_of_month, next_day_of_week]),
                           default=None)
            return (next_day_of_month
                    if self._day_of_week.is_any
                    else next_day_of_week)
        if self._mode is DaySelectionMode.AND:
            while (next_day_of_month is not None
                   and next_day_of_week is not None):
                if next_day_of_month < next_day_of_week:
                    next_day_of_month = self._day_of_month.next(
                            year, month, next_day_of_month)
                elif next_day_of_month > next_day_of_week:
                    next_day_of_week = self._day_of_week.next(
                            year, month, next_day_of_week)
                else:
                    return next_day_of_month
        if self._mode is DaySelectionMode.EITHER:
            return (next_day_of_month
                    if self._day_of_week.is_blank
                    else next_day_of_week)
        return None

    def is_selected(self, year: int, month: int, day: int) -> bool:
        is_selected_month = self._day_of_month.is_selected(year, month, day)
        is_selected_week = self._day_of_week.is_selected(year, month, day)
        if self._mode is DaySelectionMode.EITHER:
            return (is_selected_month
                    if self._day_of_week.is_blank
                    else is_selected_week)
        if not self._day_of_month.is_any and not self._day_of_week.is_any:
            return (is_selected_month or is_selected_week
                    if self._mode is DaySelectionMode.OR
                    else is_selected_month and is_selected_week)
        return (is_selected_month
                if self._day_of_week.is_any
                else is_selected_week)
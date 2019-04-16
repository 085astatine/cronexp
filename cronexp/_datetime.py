# -*- coding: utf-8 -*-

import calendar
from typing import NamedTuple, Optional
from ._field import Field, month_word_set, weekday_word_set


class TimeexpNext(NamedTuple):
    minute: int
    hour: int
    move_up: bool


class DateexpNext(NamedTuple):
    day: int
    month: int
    year: int


class Timeexp:
    def __init__(self, minute: str, hour: str) -> None:
        self._minute = Field(minute, 0, 59)
        self._hour = Field(hour, 0, 23)

    def next(self, hour: int, minute: int) -> TimeexpNext:
        def impl(hour_: int, minute_: int, move_up_: bool) -> TimeexpNext:
            if not self._hour.is_selected(hour_):
                next_hour = self._hour.next(hour)
                return TimeexpNext(
                        hour=next_hour.value,
                        minute=self._minute.min(),
                        move_up=move_up_ or next_hour.move_up)
            else:
                next_minute = self._minute.next(minute_)
                if next_minute.move_up:
                    hour_ += 1
                if self._hour.is_selected(hour_):
                    return TimeexpNext(
                            hour=hour_,
                            minute=next_minute.value,
                            move_up=move_up_)
                else:
                    return impl(hour_, next_minute.value, move_up_)
        return impl(hour, minute, False)

    def is_selected(self, hour: int, minute: int) -> bool:
        return (self._hour.is_selected(hour)
                and self._minute.is_selected(minute))


class Dateexp:
    def __init__(
            self,
            day: str,
            month: str,
            weekday: str) -> None:
        self._day = Field(day, 1, 31)
        self._month = Field(month, 1, 12, word_set=month_word_set())
        # 0: sunday, ..., 6: saturday
        self._weekday = Field(weekday, 0, 6, word_set=weekday_word_set())

    def next(self, day: int, month: int, year: int) -> DateexpNext:
        def next_day(
                year_: int,
                month_: int,
                day_: Optional[int]) -> Optional[int]:
            for day__ in range(1, calendar.monthrange(year_, month_)[1] + 1):
                if day_ is not None and day__ <= day_:
                    continue
                if self.is_selected(year_, month_, day__):
                    return day__
            else:
                return None

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
                else:
                    day_ = next_day(year_, month_, day_)
                    if day_ is not None:
                        return DateexpNext(year=year_, month=month_, day=day_)
                    else:
                        month_ += 1
            else:
                day_ = next_day(year_, month_, day_)
                if day_ is not None:
                    return DateexpNext(year=year_, month=month_, day=day_)
                else:
                    month_ += 1
            return impl(year_, month_, day_)

        return impl(year, month, day)

    def is_selected(self, year: int, month: int, day: int) -> bool:
        if not self._month.is_selected(month):
            return False
        try:
            # 0: monday, ...., 6: sunday -> 0: sunday, ..., 6: saturday
            weekday = (calendar.weekday(year, month, day) + 1) % 7
        except ValueError:
            return False
        if self._day.is_any and self._weekday.is_any:
            return True
        elif self._day.is_any and not self._weekday.is_any:
            return self._weekday.is_selected(weekday)
        elif not self._day.is_any and self._weekday.is_any:
            return self._day.is_selected(day)
        else:
            return (self._day.is_selected(day)
                    or self._weekday.is_selected(weekday))

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

    def next(self, minute: int, hour: int) -> TimeexpNext:
        def impl(minute_: int, hour_: int, move_up_: bool) -> TimeexpNext:
            if not self._hour.is_selected(hour_):
                next_hour = self._hour.next(hour)
                return TimeexpNext(
                        minute=self._minute.min(),
                        hour=next_hour.value,
                        move_up=move_up_ or next_hour.move_up)
            else:
                next_minute = self._minute.next(minute_)
                if next_minute.move_up:
                    hour_ += 1
                if self._hour.is_selected(hour_):
                    return TimeexpNext(
                            minute=next_minute.value,
                            hour=hour_,
                            move_up=move_up_)
                else:
                    return impl(next_minute.value, hour_, move_up_)
        return impl(minute, hour, False)

    def is_selected(self, minute: int, hour: int) -> bool:
        return (self._minute.is_selected(minute)
                and self._hour.is_selected(hour))


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
                day_: Optional[int],
                month_: int,
                year_: int) -> Optional[int]:
            for day__ in range(1, calendar.monthrange(year_, month_)[1] + 1):
                if day_ is not None and day__ <= day_:
                    continue
                if self.is_selected(day__, month_, year_):
                    return day__
            else:
                return None

        def impl(
                day_: Optional[int],
                month_: int,
                year_: int) -> DateexpNext:
            if not self._month.is_selected(month_):
                next_month = self._month.next(month_)
                if next_month.move_up:
                    return impl(None, next_month.value, year_ + 1)
                else:
                    next_day_ = next_day(None, next_month.value, year_)
                    if next_day_ is not None:
                        return DateexpNext(
                                day=next_day_,
                                month=next_month.value,
                                year=year_)
                    else:
                        return impl(None, next_month.value + 1, year_)
            else:
                day_ = next_day(day_, month_, year_)
                if day_ is not None:
                    return DateexpNext(
                            day=day_,
                            month=month_,
                            year=year_)
                else:
                    return impl(None, month_ + 1, year_)

        return impl(day, month, year)

    def is_selected(self, day: int, month: int, year: int) -> bool:
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

# -*- coding: utf-8 -*-

from typing import NamedTuple, Optional
from ._field import Field


class TimeexpNext(NamedTuple):
    minute: int
    hour: int
    move_up: bool


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

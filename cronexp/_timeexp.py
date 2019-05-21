# -*- coding: utf-8 -*-

from typing import NamedTuple
from ._field import Field


class TimeexpNext(NamedTuple):
    minute: int
    hour: int
    move_up: bool


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

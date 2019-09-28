# -*- coding: utf-8 -*-

from typing import NamedTuple, Optional
from ._dayexp import DaySelectionMode
from ._weekday_field import SundayMode


class CronexpOption(NamedTuple):
    max_year: Optional[int] = None
    use_word_set: bool = True
    day_selection_mode: DaySelectionMode = DaySelectionMode.OR
    sunday_mode: SundayMode = SundayMode.SUNDAY_IS_0

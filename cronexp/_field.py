# -*- coding: utf-8 -*-

from typing import Dict, NamedTuple, Optional
from ._field_parser import FieldParser


class FieldNext(NamedTuple):
    value: int
    move_up: bool


class Field:
    def __init__(
            self,
            field: str,
            min_: int,
            max_: int,
            word_set: Optional[Dict[str, int]] = None) -> None:
        parser = FieldParser(field, min_, max_, word_set=word_set)
        result = parser.parse_field()
        self._is_any = result.is_any
        self._value = result.value
        assert(len(self._value) != 0)

    @property
    def is_any(self) -> bool:
        return self._is_any

    def next(self, value: int) -> FieldNext:
        next_value: Optional[int] = None
        for i in self._value:
            if value < i:
                next_value = i
                break
        return FieldNext(
            value=next_value if next_value is not None else self.min(),
            move_up=next_value is None)

    def is_selected(self, i: int) -> bool:
        return i in self._value

    def min(self) -> int:
        return min(self._value)

    def max(self) -> int:
        return max(self._value)

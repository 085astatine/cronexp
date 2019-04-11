# -*- coding: utf-8 -*-

import re
from typing import List, Optional


def evaluate_field(
        min_: int,
        max_: int,
        begin: Optional[int],
        end: Optional[int],
        step: Optional[int]) -> List[int]:
    result: List[int] = []
    if step is None:
        if begin is None:
            result.extend(range(min_, max_ + 1))
        else:
            if end is None:
                result.append(begin)
            else:
                result.extend(range(begin, end + 1))
    else:
        init = begin if begin is not None else min_
        last = end if end is not None else max_
        if init < last and 0 < step:
            value = init
            while value <= last:
                result.append(value)
                value += step
    return result


def parse_field(
        field: str,
        min_: int,
        max_: int) -> List[int]:
    target: List[int] = []
    pattern = re.compile(
            r'^((?P<any>\*)|(?P<begin>[0-9]+)(|-(?P<end>[0-9]+)))'
            r'(|/(?P<step>[0-9]+))$')
    for x in field.split(','):
        match = pattern.match(x)
        if not match:
            continue
        begin: Optional[int] = (
                int(match.group('begin'))
                if match.group('begin') is not None else None)
        end: Optional[int] = (
                int(match.group('end'))
                if match.group('end') is not None else None)
        step: Optional[int] = (
                int(match.group('step'))
                if match.group('step') is not None else None)
        # evaluate
        target.extend(evaluate_field(
                min_,
                max_,
                begin,
                end,
                step))
    # sort & unique
    return sorted(set(target))

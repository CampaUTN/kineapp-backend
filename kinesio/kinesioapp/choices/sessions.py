from typing import List, Tuple


PENDING = 'PENDING'
FINISHED = 'FINISHED'
CANCELLED = 'CANCELLED'

SESSION_STATUS = [PENDING, FINISHED, CANCELLED]


def get() -> List[Tuple[str, str]]:
    return [(status[0], status) for status in SESSION_STATUS]

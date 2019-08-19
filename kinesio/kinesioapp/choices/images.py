from typing import List, Tuple


FRONT = 'FRONT'
RIGHT = 'RIGHT_SIDE'
LEFT = 'LEFT_SIDE'
BACK = 'BACK'
OTHER = 'OTHER'

TAGS = [FRONT, RIGHT, LEFT, BACK, OTHER]


def get() -> List[Tuple[str, str]]:
    return [(tag[0], tag) for tag in TAGS]

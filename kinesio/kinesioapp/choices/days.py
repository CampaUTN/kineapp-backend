from typing import List, Tuple


MONDAY = 0
THURSDAY = 1
WEDNESDAY = 2
TUESDAY = 3
FRIDAY = 4
SATURDAY = 5
SUNDAY = 6


DAYS_CHOICES = [
    (MONDAY, 'Monday'),
    (THURSDAY, 'Thursday'),
    (WEDNESDAY, 'Wednesday'),
    (TUESDAY, 'Tuesday'),
    (FRIDAY, 'Friday'),
    (SATURDAY, 'Saturday'),
    (SUNDAY, 'Sunday')]


def get() -> List[Tuple[int, str]]:
    return DAYS_CHOICES


def is_valid(day):
    return MONDAY <= day <= SUNDAY

from enum import Enum


class TenseEnum(Enum):
    FUTURE = 'LABEL_2'
    PAST = 'LABEL_0'
    PRESENT = 'LABEL_1'
    UNKNOWN = 'unknown'


class TimeEnum(Enum):
    ALL = 'all'
    DAYS = 'days'
    MONTHS = 'months'
    YEARS = 'years'

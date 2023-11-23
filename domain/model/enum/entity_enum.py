from enum import Enum


class KeywordsEnum(Enum):
    ROOM = ['salle', 'espace']


class EntityGroupType(Enum):
    COMPONENT = 'COMPONENT'
    LOC = 'LOC'
    MEASURE = 'MEASURE'
    METRIC = 'METRIC'
    STATISTIC = 'STATISTIC'


class MetricMappingEnum(Enum):
    BOOL = '.'
    BOOLEAN = '.'
    DEGREES = 'degrés'
    INTEGER = '.'
    LUMENS = 'lumens'
    MILLIVOLTS = 'millivolts'
    PERCEMTS = '%'
    PERCENTAGE = '%'
    PERCENTS = '%'
    PPM = 'ppm'


class TimeMappingEnum(Enum):
    YEARS = 'années'
    MONTHS = 'mois'
    DAYS = 'jours'

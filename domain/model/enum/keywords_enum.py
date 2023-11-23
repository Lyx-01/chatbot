# Contains a list of specific keywords extracted from sensor names
from enum import Enum


class RoomEnum(Enum):
    BUILDING = ['building', 'batiment']
    CANTEEN = ['canteen', 'cantine']
    CETIC_SPACE = ['espacecetic']
    ENIAC = ['Eniac']
    EXTERNAL = ['external', 'extérieur']
    GROUND_FLOOR = ['ground_floor']
    SECRETARIAT = ['secrétariat']
    TURING = ['Turing']
    UNDERFLOOR = ['underfloor']


class ComponentEnum(Enum):
    EXTRACT_FAN = ['extract_fan']
    FAN = ['fan', 'ventilateur']
    FAN_COIL = ['fancoil', 'ventilo-convecteur']
    FRONT = ['front']
    INFLOW = ['inflow']
    OUTFLOW = ['outflow']
    PAC = ['pac']
    REGULATOR = ['regulator', 'régulateur']
    REGULATOR_CONTROLLED_VARIABLE = ['regulator_controlled_variable']
    REGULATOR_SETPOINT = ['regulator_setpoint']
    VALVE = ['valve', 'vanne']
    WATER = ['water', 'eau']


class MeasureEnum(Enum):
    BATT = ['batt', 'batterie']
    CHANGEOVER = ['changeover']
    CO1 = ['CO1']
    CO2 = ['CO2', 'co2']
    HUMIDITY = ['humidity', 'humidité']
    HYSTERESIS = ['hysteresis', 'hystérésis']
    LUMINOSITY = ['luminosity', 'luminosité']
    MAX_OUTPUT = ['max_output']
    POWER = ['power', 'puissance']
    PSV = ['psv']
    STATUS = ['state', 'status', 'état', 'statut']
    TEMPERATURE = ['temp', 'température']
    TEMPERATURE_THRESHOLD = ['temperature_threshold']
    TIMECONSTATNT_IN = ['timeconstant_in']
    TIMECONSTATNT_OUT = ['timeconstant_out']
    VALUE = ['value', 'valeur']


class MetricEnum(Enum):
    BOOLEAN = ['boolean', 'booléen']
    DEGREES = ['degrees', 'degré']
    INTEGER = ['integer']
    LUMENS = ['lumens']
    MILLIVOLTS = ['millivolts']
    PERCENT = ['percentage', 'percents', 'percemts', 'pourcentage']
    PPM = ['ppm']


class StatisticEnum(Enum):
    MEAN = ['mean', 'moyenne']
    MEDIAN = ['median', 'médiane']
    STANDARD_DEVIATION = ['standard_deviation', 'écart-type']
    VARIANCE = ['variance']

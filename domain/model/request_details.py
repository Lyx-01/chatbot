from NLP.domain.model.enum.keywords_enum import *


class RequestDetails:
    def __init__(self,
                 room_name=None,
                 component=None,
                 metric=None,
                 measure=None,
                 value=None,
                 statistic=None
                 ):
        self.room = room_name
        self.component = component
        self.metric = metric
        self.measure = measure
        self.value = value
        self.statistic = statistic
        self.messages = []
        self.parquets = []
        self.error_counts = 0
        self.default_error_message_number = 2

    def get_request_details(self):
        attributes = []
        if self.room is not None:
            attributes.append(f"room={self.room}")
        if self.component is not None:
            attributes.append(f"component={self.component}")
        if self.metric is not None:
            attributes.append(f"metric={self.metric}")
        if self.measure is not None:
            attributes.append(f"measure={self.measure}")
        if self.statistic is not None:
            attributes.append(f"statistic={self.statistic}")
        if self.value is not None:
            attributes.append(f"value={self.value}")
        attributes.append(f"messages={self.messages}")
        attributes.append(f"error_counts={self.error_counts}")
        attributes.append(f"default_error_message_number={self.default_error_message_number}")

        return f"RequestDetails({', '.join(attributes)})"

    # Setters
    def set_message(self, msg):
        self.messages = [msg]

    def get_mandatory_arguments(self):
        return [
            (self.room, "ROOM"),
            (self.measure, "MEASURE")
        ]

    def attributes_and_enums(self):
        return [
            (self.room, RoomEnum, "ROOM"),
            (self.component, ComponentEnum, "COMPONENT"),
            (self.measure, MeasureEnum, "MEASURE"),
            (self.metric, MetricEnum, "METRIC"),
            (self.statistic, StatisticEnum, "STATISTIC")
        ]

    def add_message(self, msg):
        self.messages.append(msg)

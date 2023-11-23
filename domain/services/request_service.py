from datetime import datetime
import requests
from unidecode import unidecode

from NLP.domain.model.enum.message_type_enum import ErrorMessage, OutputType, AnswerMessage
from NLP.domain.model.request_details import RequestDetails
from NLP.domain.services.repository.request_repository import RequestRepository


class RequestService:
    def __init__(self,
                 user_request_repository: RequestRepository,
                 tsorage_api: dict
                 ):
        self.user_request_repository = user_request_repository
        self.tsorage_api = tsorage_api

    def get_all_requests(self):
        return self.user_request_repository.get_all_requests()

    def add_request(self, room_name: str, component: str, measure: str, metric: str, statistic: str):
        return self.user_request_repository.add_request(
            RequestDetails(
                room_name=room_name,
                component=component,
                measure=measure,
                metric=metric,
                statistic=statistic
            )
        )

    def set_all_requests(self, requests: list[RequestDetails]):
        self.user_request_repository.set_all_requests(requests)

    def add_general_request_message(self, msg):
        self.user_request_repository.add_general_request_message(msg)

    def set_general_request_message(self, msg):
        self.user_request_repository.set_general_request_message(msg)

    def get_general_request_message(self):
        return self.user_request_repository.get_general_request_message()

    def get_general_formatted_request_message(self):
        return {"type_message": OutputType.TEXT,
                "message": '\n'.join(msg['message'] for msg in self.get_general_request_message())}

    @staticmethod
    def check_enum_exists(value: str, enum_type):
        """
        Check if the provided value exists in the specified enumeration type.

        :param value: str The value to check for existence in the enumeration.
        :param enum_type: Enum
            The enumeration type to check against.
        :return: Enum member or None: If the value exists in the enumeration, returns the corresponding enum member.
            If not found, returns None.
        """
        value_normalized = unidecode(value).lower()
        for enum_member in enum_type:
            if value_normalized in (unidecode(val).lower() for val in enum_member.value):
                return enum_member
        return None

    # Check functions
    def check_entity_exists(self, request: RequestDetails, entity: str, entity_enum, name: str):
        """
        Check if the provided entity exists in the given enumeration.

        :param request: RequestDetails.
            The request to check
        :param entity: str
            The entity to check for existence.
        :param entity_enum: Enum
            The enumeration to check against.
        :param name: str
            The attribute to update.
        :return: True if the entity exists, False otherwise.
        """

        result = self.check_enum_exists(entity, entity_enum)
        if result:
            setattr(request, name.lower(), result)
            return True
        return False

    def check_request_arguments(self, request: RequestDetails):
        """
        Checks whether all arguments of the request are correct and are existing to get the parquet data. It refuses the
        request if there is an error and send a personalized message if there is a few errors but send a default message
        if there are too many missing arguments

        :param request: RequestDetails. The request to check.
        :return: Returns a boolean indicating whether the request can be processed or not and the messages associated
        when there is an error.
        """

        # Check for mandatory arguments
        mandatory_enums = request.get_mandatory_arguments()
        mandatory_arg_missing = 0
        for argument, enum_type in mandatory_enums:
            if argument is None:
                request.error_counts += 1
                missing_enum_name = f'{enum_type}_MISSING'
                self.user_request_repository.add_request_message(
                    request,
                    {"type_message": OutputType.ERROR, "message": getattr(ErrorMessage, missing_enum_name).value}
                )
                mandatory_arg_missing += 1
        if mandatory_arg_missing:
            return False, self.user_request_repository.return_message(request)

        # check request arguments
        attributes_and_enums = self.user_request_repository.get_attributes_and_enums(request)
        # Check existence for each attribute
        for attribute, enum_type, name in attributes_and_enums:
            if attribute is not None and not self.check_entity_exists(request, attribute, enum_type, name):
                self.user_request_repository.add_error_message(
                    request,
                    getattr(ErrorMessage, f'{name.upper()}_UNK').value,
                    attribute
                )
                request.error_counts += 1

        # too many arguments that do not exist, ask to reformulate the request
        if request.error_counts >= request.default_error_message_number:
            self.user_request_repository.set_request_message(
                request,
                {
                    "type_message": OutputType.TEXT,
                    "message": ErrorMessage.ARGS_UNK.value
                }
            )
            return False, self.user_request_repository.get_request_message(request)

        if request.error_counts:
            return False, self.user_request_repository.return_message(request)
        return True, None

    def check_parquet(self, request: RequestDetails):
        """
         Checks parquet data and updates error counts and messages if there is not one parquet for the request.

        :param request: RequestDetails.
            The request parquets tp check.
        :return: None
        """

        if not request.parquets:
            request.error_counts += 1
            self.add_general_request_message({"type_message": OutputType.ERROR,
                                              "message": ErrorMessage.PARQUET_NOT_FOUND.value})
        if len(request.parquets) > 1:
            request.error_counts += 1
            self.add_general_request_message({"type_message": OutputType.ERROR,
                                              "message": ErrorMessage.PARQUET_PRECISE.value})

    def get_data_from_api(self, captor: str, start: str, end: str):
        """
        Performs a request to an API using the specified parameters and retrieves sensor data.

        :param captor: str.
            The sensor for the request. It is the parquet name.
        :param start: str.
            Start date of the request in the required format by the API.
        :param end: str.
            End date of the request in the required format by the API.
        :return: Returns the data retrieved from the API in JSON format, or None if the request fails.
        """
        url = f"{self.tsorage_api['base_url'].removesuffix('/') + '/'}{self.tsorage_api['sensor_url']}"
        url_query = (f"{self.tsorage_api['query_params']['query']}={captor}"
                     f"{self.tsorage_api['query_params']['start']}={start}"
                     f"{self.tsorage_api['query_params']['end']}={end}")
        response = requests.get(url + url_query, headers=self.tsorage_api['headers'], verify=False)

        if response.status_code == 200:
            return response.json()
        else:
            return None

    def get_sensor_data(self, request: RequestDetails):
        """
        Retrieves sensor data based on the provided request details.
        :param request: RequestDetails.
            The request containing all the details.
        :return: Returns a message containing either the retrieved sensor data or an error message.
        """
        current_date = datetime.now()
        # Get date at midnight
        date_at_midnight = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
        current_timestamp = current_date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + 'Z'
        today_timestamp = date_at_midnight.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + 'Z'
        data = self.get_data_from_api(request.parquets[0], today_timestamp, current_timestamp)
        if data and data['data']['result']:
            res = data['data']['result'][0]['values'][-1][-1]
            return {"type_message": OutputType.TEXT,
                    "message": AnswerMessage.VALUE.value.format(
                        res,
                        request.measure.value[-1],
                        request.room.value[-1]
                    ).removesuffix('.') + '.'
                    }
        return {"type_message": OutputType.ERROR,
                "message": AnswerMessage.NO_VALUE.value.format(
                    request.measure.value[-1],
                    request.room.value[-1]
                ).removesuffix('.') + '.'
                }

from collections import Counter
from NLP.domain.model.enum.entity_enum import EntityGroupType
from NLP.domain.model.enum.message_type_enum import ErrorMessage, OutputType
from NLP.domain.model.enum.model_enum import TenseEnum, TimeEnum
from NLP.domain.services.entity_extractor_service import EntityExtractorService
from NLP.domain.services.file_extractor_service import FileExtractorService
from NLP.domain.services.model_service import ModelService
from NLP.domain.services.request_service import RequestService
from NLP.domain.services.statistics_service import StatisticsService


class ChatbotService:
    def __init__(self,
                 extractor_service: EntityExtractorService,
                 request_service: RequestService,
                 file_extractor_service: FileExtractorService,
                 statistics_service: StatisticsService,
                 model_service: ModelService):
        self.extractor_service = extractor_service
        self.request_service = request_service
        self.file_extractor_service = file_extractor_service
        self.model_service = model_service
        self.statistics_service = statistics_service

    def check_request_number_arguments(self):
        """
        Check the number of arguments in the requests and detect potential errors.
        It will indicate errors when specific criteria are not fulfilled.

        :param: None
        :returns: A boolean indicating whether the conditions are satisfied or not, along with an associated message.
        """
        entity_counts = Counter(entity_type for entry in self.extractor_service.get_extracted_entities()
                                for entity_type in entry.keys()
                                )
        # no arguments recognized
        if not entity_counts:
            return False, self.send_reformulation_message(ErrorMessage.REQ_UNK.name)
        # only have one argument
        if len(self.extractor_service.get_extracted_entities()) < 2:
            return False, self.send_reformulation_message(ErrorMessage.INSUFFICIENT_ARGS.name)
        for entity, count in entity_counts.items():
            # Too many elements
            if count > 1:
                return False, self.send_reformulation_message(EntityGroupType(entity).value)

        # number of arguments are correct
        return True, None

    def verify_number_arguments(self):
        """
        This method checks if all the required arguments in the user's request are correctly specified.

        :return: Returns a boolean indicating whether the user's request arguments are accurately provided.
        """

        is_precondition_valid, error_message = self.check_request_number_arguments()
        if not is_precondition_valid:
            return False, error_message

        # create all requests
        # to change if several requests can be made in one input
        keys_to_extract = [member for member in EntityGroupType]
        values = {key: None for key in keys_to_extract}

        for entity in self.extractor_service.get_extracted_entities():
            for key in keys_to_extract:
                values[key] = entity.get(key, values[key])

        self.request_service.add_request(room_name=values[EntityGroupType.LOC],
                                         component=values[EntityGroupType.COMPONENT],
                                         measure=values[EntityGroupType.MEASURE],
                                         metric=values[EntityGroupType.METRIC],
                                         statistic=values[EntityGroupType.STATISTIC]
                                         )

        return True, None

    def check_requests(self):
        """
        Validates each request in the chatbot's list of requests.
        For each request, it prints the request details, checks the validity of its arguments, and collects messages.
        Invalid requests are marked, and unnecessary ones are removed.

        :return: Returns a tuple (bool, messages) indicating whether all requests are valid.
             If not, it returns False and a list of messages associated with the invalid requests.
             If there are too many invalid requests, a default error message is returned.
             If all requests are valid, it returns True and None.
        """
        requests_refused_count = 0
        default_number_message_refused = 2

        for request in self.request_service.get_all_requests():
            is_request_valid, messages = self.request_service.check_request_arguments(request)
            if not is_request_valid:
                requests_refused_count += 1
                self.request_service.add_general_request_message(messages)
                continue
        # Remove unnecessary requests
        self.remove_invalid_request()
        # Optional: for several requests in one input
        if requests_refused_count >= default_number_message_refused:
            self.request_service.set_general_request_message({
                "type_message": OutputType.TEXT,
                "message": ErrorMessage.ARGS_UNK.value
            })
            return False, self.request_service.get_general_request_message()
        return True, None

    def find_accepted_requests(self):
        """
        Finds and returns a list of accepted requests among the chatbot requests.
        It iterates through each request and checks if it has any errors.
        If a request has no errors (error_counts is zero), it is considered accepted and added to the list.

        :return: Returns a list of accepted requests.
        """
        accepted_req = []
        for req in self.request_service.get_all_requests():
            if not req.error_counts:
                accepted_req.append(req)
        return accepted_req

    def remove_invalid_request(self):
        """
        Removes invalid requests from the chatbot list of requests.
        :return: None
        """
        accepted_req = self.find_accepted_requests()
        self.request_service.set_all_requests([request for request in accepted_req])

    def find_valid_parquets(self):
        """
        Checks for all requests whether a parquet is found and checks whether it is correct or not.
        Finally, it removes any invalid requests.
        :return: None
        """
        self.file_extractor_service.find_parquets(self.request_service.get_all_requests())
        list(map(self.request_service.check_parquet, self.request_service.get_all_requests()))
        self.remove_invalid_request()

    def compute_data(self, tense: TenseEnum, request_input: str):
        """
        Analyzes the input request to generate statistical data or error messages based on the specified tense.

        This function processes the request based on the specified time (past or otherwise).
        It analyzes the input request, identifies a time period and an associated number, then uses available services
        to generate statistics or error messages.
        :param tense: TenseEnum.
            Enum describing the specified time for analysis (PAST, PRESENT, FUTURE, UNKNOWN).
        :param request_input: str.
            String representing the request to be analyzed.
        :return: None
        """
        # to change if several requests can be made
        period, number_for_period = self.model_service.identify_period(request_input)
        tense_period_functions = {
            TenseEnum.PAST: self.statistics_service.make_statistic,
            TenseEnum.FUTURE: self.statistics_service.make_prediction
        }
        for req in self.request_service.get_all_requests():
            if tense in tense_period_functions:
                period_is_valid = self.check_period(period, number_for_period)
                if not period_is_valid:
                    continue
                self.request_service.add_general_request_message(
                    tense_period_functions[tense](req, period, number_for_period[0])
                )
            elif tense == TenseEnum.PRESENT:
                self.request_service.add_general_request_message(
                    self.request_service.get_sensor_data(request=req)
                )
            else:
                self.request_service.add_general_request_message(
                    {"type_message": OutputType.TEXT,
                     "message": ErrorMessage.TENSE_UNK.value + ErrorMessage.REITERATE_REQ.value
                     }
                )

    def check_period(self, period: TimeEnum, number_for_period: list[int]):
        """
        Validates the period and the list of numbers associated with it.
        - If the period is 'all', it is considered valid (returns True).
        - If the length of number_for_period is greater than 1, it is considered invalid.
          - In this case, it adds an error message for NUMBER_PERIOD_EXCEED and returns False.
        - If the number_for_period list is empty, it is considered invalid.
          - In this case, it adds an error message for NUMBER_PERIOD_UNK and returns False.
        - If none of the above conditions are met, it is considered valid (returns True).

        :param period: TimeEnum.
            The time period to be validated.
        :param number_for_period: list[int].
             List of numbers associated with the period.
        :return: returns a boolean. True if the period and number_for_period are valid, False otherwise.
        """
        if period == TimeEnum.ALL:
            return True
        if len(number_for_period) > 1:
            self.request_service.add_general_request_message(
                {"type_message": OutputType.TEXT, "message": ErrorMessage.NUMBER_PERIOD_EXCEED.value}
            )
            return False
        if not number_for_period:
            self.request_service.add_general_request_message(
                {"type_message": OutputType.TEXT, "message": ErrorMessage.NUMBER_PERIOD_UNK.value}
            )
            return False
        return True

    def send_reformulation_message(self, entity: str, arg=None):
        """
        Generates a reformulation message based on the provided entity and optional argument.
        This function creates a reformulation message, typically used to inform the user about specific issues or
        errors in their request.
        :param entity: str
            The type of entity or error identifier for which the message is generated.

        :param arg: str, optional
            An optional argument that can be used to provide additional information in the message.

        :return: Returns a dictionary containing the reformulation message with a type and message content.
        """

        self.extractor_service.clear_extracted_entities()
        return {"type_message": OutputType.TEXT, "message": ErrorMessage[entity].value.format(arg)}

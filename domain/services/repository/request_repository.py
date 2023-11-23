from abc import abstractmethod, ABC

from NLP.domain.model.enum.entity_enum import EntityGroupType
from NLP.domain.model.request_details import RequestDetails


class RequestRepository(ABC):
    @abstractmethod
    def get_extracted_entities(self):
        pass

    def clear_extracted_entities(self):
        pass

    @abstractmethod
    def add_entity_from_room_name(self, room_name: str):
        pass

    @abstractmethod
    def add_entity_from_room_keyword(self, possible_room_name: list[str]):
        pass

    @abstractmethod
    def add_entity_from_keyword(self, entity_type: EntityGroupType, keyword: str):
        pass

    @abstractmethod
    def get_all_requests(self):
        pass

    def set_all_requests(self, requests: list[RequestDetails]):
        pass

    @abstractmethod
    def add_request(self, request: RequestDetails):
        pass

    @abstractmethod
    def get_attributes_and_enums(self, request: RequestDetails):
        pass

    @abstractmethod
    def add_general_request_message(self, msg):
        pass

    @abstractmethod
    def set_general_request_message(self, msg):
        pass

    @abstractmethod
    def get_general_request_message(self):
        pass

    @abstractmethod
    def add_request_message(self, request: RequestDetails, msg):
        pass

    @abstractmethod
    def get_request_message(self, request: RequestDetails):
        pass

    @abstractmethod
    def set_request_message(self, request: RequestDetails, msg):
        pass

    @abstractmethod
    def add_error_message(self, request: RequestDetails, error_enum: str, arg=None):
        pass

    @abstractmethod
    def return_message(self, request: RequestDetails):
        pass

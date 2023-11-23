from NLP.domain.model.enum.entity_enum import EntityGroupType
from NLP.domain.model.enum.keywords_enum import RoomEnum
from NLP.domain.model.enum.message_type_enum import OutputType, ErrorMessage
from NLP.domain.model.request_details import RequestDetails
from NLP.domain.services.repository.request_repository import RequestRepository


class UserRequestsRepository(RequestRepository):
    def __init__(self) -> None:
        self.identified_keywords = []
        self.requests: list[RequestDetails] = []
        self.requests_msg = []

    # Getters
    def get_extracted_entities(self):
        return self.identified_keywords

    def clear_extracted_entities(self):
        self.identified_keywords = []

    def add_entity_from_room_name(self, room_name: str) -> None:
        """
        Appends the room name as a keyword along with its label **LOC** to a list.

        :param room_name: str
            The name of the room to be added as a keyword.
        :return: None
        """
        if room_name not in [entity.get(EntityGroupType.LOC, None) for entity in self.identified_keywords]:
            format_entity = {
                EntityGroupType.LOC: room_name
            }
            self.identified_keywords.append(format_entity)

    def add_entity_from_room_keyword(self, possible_room_name: list[str]):
        """
        This function processes a list of words to extract a possible room name and adds it as a location entity to the
        list of identified keywords if it doesn't already exist.

        :param possible_room_name: list[str]
            A list of words that may constitute a room name.
        :return: None
        """

        room_name = ""
        for i, word in enumerate(possible_room_name):
            if possible_room_name[i + 1].lower() == "de":
                continue

            if i < len(possible_room_name) - 1 and word + possible_room_name[i + 1] == RoomEnum.CETIC_SPACE.value[0]:
                room_name = word + possible_room_name[i + 1]
                break

            # should be the next word after keyword 'salle'
            room_name = possible_room_name[i + 1]
            break

        if room_name not in [entity.get(EntityGroupType.LOC, None) for entity in self.identified_keywords]:
            format_entity = {
                EntityGroupType.LOC: room_name
            }
            self.identified_keywords.append(format_entity)

    def add_entity_from_keyword(self, entity_type: EntityGroupType, keyword: str):
        """
        Appends the specified keyword along with its associated label to the list of identified keywords

        :param entity_type: EntityGroupType
            The type of entity label associated with the keyword.
        :param keyword: str
            The keyword to be added to the list of identified keywords.
        :return: None
        """
        if keyword not in [entity.get(entity_type, None) for entity in self.identified_keywords]:
            format_entity = {
                entity_type: keyword
            }
            self.identified_keywords.append(format_entity)

    def get_all_requests(self):
        """
        Retrieves all requests

        :return: A list containing all requests
        :rtype: list[RequestDetails]
        """
        return self.requests

    def add_request(self, req: RequestDetails):
        """
        Add new request

        :param req: RequestDetails. A user's request
        :return: None
        """
        self.requests.append(req)

    def set_all_requests(self, requests: list[RequestDetails]):
        """
        Sets requests
        :param requests: list[RequestDetails]
            Requests to overwrite with
        :return: None
        """
        self.requests = requests

    def get_attributes_and_enums(self, request: RequestDetails):
        """
        Get attributes and enums associated.
        :param request: RequestDetails. The request to get attributes.
        :return: returns attributes and enums associated.
        """
        return self.requests[self.requests.index(request)].attributes_and_enums()

    def add_general_request_message(self, msg):
        """
        Adds a message for the general request asked by the user.
        :param msg: The message to add.
        :return: None
        """
        self.requests_msg.append(msg)

    def set_general_request_message(self, msg):
        """
        Sets a message for the user's input
        :param msg: The message to set
        :return: Non
        """
        self.requests_msg = [msg]

    def get_general_request_message(self):
        """
        Gets all messages of the user's input
        :return: Returns the user's request messages.
        """
        return self.requests_msg

    def add_request_message(self, request: RequestDetails, msg):
        """
        Adds a message
        :param request: RequestDetails.
            The request to which the message will be added.
        :param msg: dict.
            The message to add.
        :return:
        """
        self.requests[self.requests.index(request)].add_message(msg)

    def get_request_message(self, request: RequestDetails):
        """
        Gets a message for a specific request.

        :param request: RequestDetails.
            The request to get the message.
        :return: Returns request messages.
        """
        return self.requests[self.requests.index(request)].messages

    def set_request_message(self, request: RequestDetails, msg):
        """
        Sets a message for a specific request.
        :param request: RequestDetails.
            The request for which the message will be set.
        :param msg: The message to be set for the request.
        :return: None
        """
        self.requests[self.requests.index(request)].set_message(msg)

    def add_error_message(self, request: RequestDetails, msg: str, arg=None):
        """
        Adds an error message to a specific request within the object's stored requests.

        :param request: RequestDetails.
            The request to which the error message will be added.
        :param msg: str. The error message to be added to the request.
        :param arg: str. Argument
        :return: None
        """
        self.requests[self.requests.index(request)].add_message({
            "type_message": OutputType.ERROR,
            "message": msg.format(arg)
        })

    def return_message(self, request: RequestDetails):
        """
        Join messages together
        :return: Return all messages in one message
        """
        return {"type_message": OutputType.TEXT, "message": '\n'.join(msg['message']
                for msg in self.requests[self.requests.index(request)].messages)
                + ErrorMessage.REITERATE_REQ.value}

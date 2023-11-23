from unidecode import unidecode
from NLP.domain.model.enum.entity_enum import KeywordsEnum, EntityGroupType
from NLP.domain.model.enum.keywords_enum import *
from NLP.domain.services.repository.request_repository import RequestRepository


class EntityExtractorService:
    def __init__(self, user_requests_repository: RequestRepository):
        self.user_requests_repository = user_requests_repository
        self.room_name_search_range = 5

    def get_extracted_entities(self):
        return self.user_requests_repository.get_extracted_entities()

    def clear_extracted_entities(self):
        self.user_requests_repository.clear_extracted_entities()

    def extract_words(self, req: str):
        """
        Extracts potential words from the user's input and appends the word along with its label to the list of
        identified keywords.

        :param req: str
            The input provided by the user.
        :return: returns potential words with its label
        """
        split_request = req.replace("'", " ").split()
        split_lowercase_request = unidecode(req).lower().replace("'", " ").split()
        for word in split_lowercase_request:
            match word:
                # keyword directly identified
                case isRoomName if (
                            isRoomName in (unidecode(value).lower() for room in RoomEnum for value in room.value)):
                    self.user_requests_repository.add_entity_from_room_name(
                        split_request[split_lowercase_request.index(word)]
                    )

                # identify a specific keyword
                case isRoomKeyword if (isRoomKeyword in KeywordsEnum.ROOM.value):
                    word_index = split_lowercase_request.index(word)
                    try:
                        room_name_candidates = split_request[word_index:word_index + self.room_name_search_range]
                    except IndexError:
                        # If an "out of range" error occurs, retrieve text until the end of the sentence
                        room_name_candidates = split_request[word_index:]
                    self.user_requests_repository.add_entity_from_room_keyword(room_name_candidates)

                case isKeyword if (isKeyword in (unidecode(value).lower()
                                                 for measure in MeasureEnum
                                                 for value in measure.value)
                                   ):
                    self.user_requests_repository.add_entity_from_keyword(EntityGroupType.MEASURE, word)

                case isKeyword if (isKeyword in (unidecode(value).lower()
                                                 for component in ComponentEnum
                                                 for value in component.value)
                                   ):
                    self.user_requests_repository.add_entity_from_keyword(EntityGroupType.COMPONENT, word)

                case isKeyword if (isKeyword in (unidecode(value).lower()
                                                 for metric in MetricEnum
                                                 for value in metric.value)
                                   ):
                    self.user_requests_repository.add_entity_from_keyword(EntityGroupType.METRIC, word)

                case isKeyword if (isKeyword in (unidecode(value).lower()
                                                 for statistic in StatisticEnum
                                                 for value in statistic.value)
                                   ):
                    self.user_requests_repository.add_entity_from_keyword(EntityGroupType.STATISTIC, word)

                case _:
                    continue

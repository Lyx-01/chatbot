from unidecode import unidecode
from NLP.domain.model.request_details import RequestDetails


class FileExtractorService:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def find_parquets(self, requests: list[RequestDetails]):
        """
        Finds parquet data for a list of requests.
        It iterates through each request and identify matching lines in the file. It appends the matching lines to the
        list of parquets of the corresponding request.

        :param requests: list[RequestDetails]
            A list of RequestDetails instances containing information about the requested data.
        :return: None
        """
        list(map(self.check_for_matching_lines, requests))

    def check_for_matching_lines(self, request: RequestDetails):
        """
        Searches for lines in a file that match the criteria specified in the given request.

        :param request: RequestDetails
            An instance containing information about the requested data.
        :return: None
        """
        with open(self.file_path, 'r') as file:
            for line in file:
                if (
                        (request.room is None or any(
                            unidecode(room_value).lower() in line for room_value in request.room.value)) and
                        (request.component is None or any(
                            unidecode(component_value).lower() in line
                            for component_value in request.component.value)) and
                        (request.metric is None or any(
                            unidecode(metric_value).lower() in line for metric_value in request.metric.value)) and
                        (request.measure is None or any(
                            unidecode(measure_value).lower() in line for measure_value in request.measure.value))
                ):
                    request.parquets.append(line.removesuffix('\n'))

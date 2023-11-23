import re

from NLP.domain.model.enum.model_enum import TenseEnum, TimeEnum


class ModelService:
    def __init__(self, model_checkpoint: str):
        self.model_checkpoint = model_checkpoint
        self.tense_tokenizer = "camembert/camembert-large"

    @staticmethod
    def identify_period(request_input: str):
        """
        Identifies a time period and extracts the associated value from a list of words.
        :param request_input: str.
            The request that may contain words related to time and potentially numbers.
        :return: Tuple[TimeEnum, int].
            A tuple containing the identified time period as a TimeEnum member and the associated numerical value.
            If no specific period is identified, defaults to 'all' and 0.
        """
        periods = {"année": "years", "années": "years", "ans": "years", "mois": "months", "jours": "days"}
        words = request_input.split(" ")
        period = str(set(periods.keys()).intersection(words))[2:-2]
        if period == 't':  # case no match
            return TimeEnum.ALL, [0]

        # TODO: Extract written numbers (e.g., "one", "two") from the string and convert them into integers.
        # extract number associated to the period e.g. 2 derniers ans
        numbers = re.findall(r'\b\d+\b', request_input)
        number_for_period = [int(number) for number in numbers]

        return TimeEnum(periods[period]), number_for_period

    def identify_tense(self, request_input: str):
        """
        identification du temps lié à la demande
        simple dans un premier temps, via Bert fine tuning sur document classification après

        :param request_input: str
            The user's request
        :return: TenseEnum -
            An enumeration representing the identifies tense (PAST, PRESENT, FUTURE, or UNKNOWN)
        """

        from transformers import pipeline
        token_classifier = pipeline(
            "text-classification", model=self.model_checkpoint, tokenizer=self.tense_tokenizer)
        response = token_classifier(request_input)
        print(response)

        match response[0]['label']:
            case TenseEnum.PAST.value:
                tense = TenseEnum.PAST
            case TenseEnum.PRESENT.value:
                tense = TenseEnum.PRESENT
            case TenseEnum.FUTURE.value:
                tense = TenseEnum.FUTURE
            case _:
                tense = TenseEnum.UNKNOWN

        return tense

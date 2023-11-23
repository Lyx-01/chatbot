from enum import Enum


class AnswerMessage(Enum):
    MEAN = "La moyenne de {} dans la salle {} est de {:.6} {}."
    MEDIAN = "La médiane de {} dans la salle {} est de {:.6} {}."
    NO_VALUE = "Aucune donnée de {} n'a été trouvée dans la salle {}."
    STANDARD_DEVIATION = "L\'écart-type de {} dans la salle {} est de {:.6} {}."
    VALUE = "La valeur est de {} pour le {} dans la salle {}."
    VARIANCE = "La variance de {} dans la salle {} est de {:.6} {}."


class ErrorMessage(Enum):
    ARGS_UNK = "La demande possède plusieurs éléments non connus."
    COMPONENT = "Veuillez ne mentionner qu\'un seul composant."
    COMPONENT_UNK = "Le composant {} n\'est pas présent."
    INSUFFICIENT_ARGS = "La demande manque d'arguments, veuillez fournir plus de détails."
    LOC = 'Veuillez ne mentionner qu\'une seule salle.'
    MEASURE = 'Veuillez ne mentionner qu\'une seule mesure.'
    MEASURE_MISSING = "Préciser quelle information vous souhaitez connaître."
    MEASURE_UNK = 'La mesure {} n\'est pas reconnue.'
    METRIC = "Veuillez ne mentionner qu\'une seule métrique"
    METRIC_UNK = "La métrique {} n\'est pas reconnue."
    NUMBER_PERIOD_UNK = "La période n'a pas été identifiée. Veuillez fournir une période numérique."
    NUMBER_PERIOD_EXCEED = "Veuillez ne fournir qu'une seule période numérique."
    PARQUET_NOT_FOUND = "Nous ne possédons pas de données correspondant à votre demande."
    PARQUET_PRECISE = ("Nous possédons plusieurs données concernant votre demande, veuillez préciser "
                       "plus en détails votre demande")
    REITERATE_REQ = " Veuillez réitérer votre demande."
    REQ_ERRORS = "Votre demande possède plusieurs demandes incorrectes."
    REQ_UNK = 'La demande n\'a pas été comprise.'
    ROOM_MISSING = "Une salle doit être mentionnée."
    ROOM_UNK = 'La salle {} n\'existe pas.'
    STATISTIC = "Veuillez ne mentionner qu\'une seule demande"
    STATISTIC_UNK = "La statistique demandée n\'a pas été reconnue. Veuillez choisir une statistique parmi {}."
    TENSE_UNK = "Je n'ai pas compris votre demande."


class OutputType(Enum):
    TEXT = 1
    GRAPH_AND_TEXT = 2
    ACTION_AND_TEXT = 3
    ERROR = 4

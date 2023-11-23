# Chatbot "analyste données temporelles sur Tsorage
# Version = 0.5
# date: 2023-08-14
# Fonctionalité: reçoit une demande, identifie le temps (passé, présent et futur) et réalise une analyse si possible
# Limitations: identification sommaire des tokens, du temps, ne tient pas compte de la demande mais réalise une analyse
#              standard pour le passé et le futur, répond que pas possible pour le présent
# But: permettre au stagiaire front-end de démarrer son stage
# Appel: chatbotv0("demande)
# Input: demande formulée en Français
# Output: texte mentionnant soit le résultat de l'analyse (passé et futur) ou le fait que l'analyse n'est pas possible
#         ou que la demande n'est pas comprise
# Améliorations:
# v0.1
#    - identification de la statistique d'intérêt pour une donnée du passé à partir d'une liste fixe
#    - aggrégat des données par jour avant de faire une inférence
# v0.2 v0.3
#    - prise en compte de la période de temps demandée pour la statistique
# v0.4
#    - prendre des imports de type parquet au lieu de csv
# v0.5 Détection type d'analyse via NLP (sequence classification)
# v0.6 Renvoie un graphique (bidon à ce stade) si une statistique est donnée
# améliorations à prévoir:
# aggréger les données au niveau jour?-> quelle est la fréquence de capture des infos?
# Identifier la liste des locaux et des capteurs
# tenir compte de la durée demandée pour l'entrainement
# tenir compte de la durée demandée pour la prédiction
# Identification du temps via BERT
# avoir des sources récentes
# rafraîchir régulièrement la BD
# accès temps réel?
# améliorer le chatbot sur la partie entité nommée en utilisant NLP: détection des dates&périodes?
# tenir compte de l'ensemble du dialogue
# interagir avec l'utilisateur avant de lancer l'analyse

import json

from NLP.Enum_type_message import OutputType
from NLP.domain.services.chatbot_service import ChatbotService
from NLP.domain.services.entity_extractor_service import EntityExtractorService
from NLP.domain.services.file_extractor_service import FileExtractorService
from NLP.domain.services.model_service import ModelService
from NLP.domain.services.request_service import RequestService
from NLP.domain.services.statistics_service import StatisticsService
from NLP.infra.cache.user_request_repository import UserRequestsRepository


def identify_tense(input):
    # identification du temps lié à la demande
    # simple dans un premier temps, via Bert fine tuning sur document classification après

    from transformers import pipeline
    with open("./config/config.json") as json_conf:
        CONF = json.load(json_conf)
    # Replace this with your own checkpoint
    model_checkpoint = CONF["model_checkpoint"]
    token_classifier = pipeline(
        "text-classification", model=model_checkpoint, tokenizer="camembert/camembert-large")

    response = token_classifier(input)
    print(response)

    if response[0]['label'] == 'LABEL_0':
        tense = "past"
    elif response[0]['label'] == 'LABEL_1':
        tense = "present"
    elif response[0]['label'] == 'LABEL_2':
        tense = "future"
    else:
        tense = "unknown"

    return tense


def acces_to_data(sensor_file):
    # accès aux données
    # une source actuellement, multisource après
    import pandas as pd

    series = pd.read_parquet(sensor_file)
    turing_co2 = [i[0] for i in series.values.tolist()]
    df = pd.DataFrame({'date': series.index.tolist(), 'turing_co2': turing_co2})
    df['date'] = pd.to_datetime(df['date'], unit="s")
    df["dates"] = df["date"].dt.date
    df["times"] = df["date"].dt.time
    ts = pd.Series(df['turing_co2'].values, index=df['date'])

    return df  # dataframe is returned because time series leads to errors when making computations on date times indexes


def identify_period(words):
    periods = {"année": "years", "années": "years", "ans": "years", "mois": "months", "jours": "days"}
    period = str(set(periods.keys()).intersection(words))[2:-2]
    if period == 't':  # case no match
        return 'all', 0

    # extract number associated to the period e.g. 2 derniers ans
    number_for_period = words[0:words.index(period)][-2]
    return periods[period], int(number_for_period)


def make_prediction(words):
    # réalise la prédiction demandée
    # basique dans un premier temps (voir même pas pertinente car il faudrait avoir des unités temporelles espacées de façon régulière
    # à faire évoluer vers: détection d'entités nommées via liste fixe et/ou Bert?

    # détection entité nommée à faire ici
    # à identifier: source données utile (via local/objet et capteur), type de modele, période pour entrainement, periode pour prédiction
    #####################################

    # accès aux données
    ###################
    ts = acces_to_data('data/data_cco_od_building_20210101_20230802/data/building_room_turing_co2_ppm_0.parquet.gzip')

    # analyse à faire ici
    #####################

    from dateutil.relativedelta import relativedelta
    ts_daily = ts[["dates", "turing_co2"]].groupby("dates").mean()

    delta_time = relativedelta(days=15)

    # start_date = max(ts.index) - delta_time
    start_date = max(ts_daily.index) - delta_time
    ts_part = ts_daily[ts_daily.index >= start_date]

    # make ar model
    from statsmodels.tsa.ar_model import AutoReg

    model = AutoReg(ts_part.values, lags=1)
    model_fit = model.fit()
    # make prediction
    yhat = model_fit.predict(len(ts) + 15, len(ts) + 15)
    return {"type_message": OutputType.TEXT,
            "message": 'La valeur prédite de {} dans {} est de {:.6} {} pour dans {} jours.'.format("co2",
                                                                                                    "la salle Turing",
                                                                                                    yhat[0], "ppm", 15)}


def make_statistic(words):
    # réalise la statistique demandée
    # basique dans un premier temps (voir même pas pertinente car il faudrait avoir des unités temporelles espacées de façon régulière
    # à faire évoluer vers: détection d'entités nommées via liste fixe et/ou Bert?

    # détection entité nommée à faire ici
    #####################################

    # identification statistique
    import pandas as pd
    from dateutil.relativedelta import relativedelta

    ts_part = pd.DataFrame(
        columns=['A', 'B', 'C'])  # ts_part va contenir la série de données par après, first random names

    statistics = {"mode": ts_part.iloc[:, 1].mode(), "moyenne": ts_part.iloc[:, 1].mean(),
                  "médiane": ts_part.iloc[:, 1].median(), "variance": ts_part.iloc[:, 1].var(),
                  "écart-type": ts_part.iloc[:,
                                1].std()}  # si changement dans ce dictionaire, changer aussi sa redéfinition à la fin de la fonction

    statistic = set(statistics.keys()).intersection(words)

    if len(statistic) == 0:
        return "La statistique demandée n'a pas été reconnue. Veuillez choisir une statistique parmi {}.".format(
            ', '.join(statistics.keys()))
    elif len(statistic) > 1:
        return "Il n'est possible que de choisir une seule statistique à la fois. Veuillez choisir une statistique parmi {}.".format(
            ', '.join(statistics.keys()))

    # identification période
    period, number_for_period = identify_period(words)

    # accès aux données
    ###################
    ts = acces_to_data('data/data_cco_od_building_20210101_20230802/data/building_room_turing_co2_ppm_0.parquet.gzip')

    # analyse à faire ici
    #####################

    if period == "all":
        ts_part = ts
    else:
        delta_time = 0  # to supress warnings
        to_exec = "delta_time = relativedelta({}={})".format(period, number_for_period)
        exec(to_exec)
        if period == "years":
            delta_time = relativedelta(years=number_for_period)
        elif period == "months":
            delta_time = relativedelta(months=number_for_period)
        elif period == "days":
            delta_time = relativedelta(days=number_for_period)

        # start_date = max(ts.index) - delta_time
        start_date = max(ts.date) - delta_time
        ts_part = ts[ts["date"] >= start_date]
        # ts_part = ts[ts["date"]>=max(ts.index) - delta_time]

    statistics = {"mode": ts_part.iloc[:, 1].mode(), "moyenne": ts_part.iloc[:, 1].mean(),
                  "médiane": ts_part.iloc[:, 1].median(), "variance": ts_part.iloc[:, 1].var(),
                  "écart-type": ts_part.iloc[:, 1].std()}

    statistic = str(statistic)[2:-2]

    # crée graphique bidon en plus

    import matplotlib.pyplot as plt
    plt.plot([0, 1, 2, 3, 4], [0, 3, 5, 9, 11])
    plt.xlabel('Months')
    plt.ylabel('Books Read')
    plt.savefig('books_ready.png')

    return {"type_message": OutputType.GRAPH_AND_TEXT,
            "message": "Le/la/l' {} de {} dans {} est de {:.6} {}.".format(statistic, "co2", "la salle Turing",
                                                                           statistics[statistic], "ppm"),
            'link_image': 'books_read.png'}


def chatbotv0(input):
    import sys
    assert sys.version >= "3.10"
    # Repository initialization
    user_requests_repository = UserRequestsRepository()

    # Service initialization
    text_extractor_service = EntityExtractorService(user_requests_repository)
    with open("NLP/config/config.json") as json_conf:
        CONF = json.load(json_conf)
    request_service = RequestService(user_request_repository=user_requests_repository, tsorage_api=CONF["tsorage_api"])
    file_extractor_service = FileExtractorService(file_path=CONF['prometheus_sensor_file_path'])
    model_service = ModelService(CONF['model_checkpoint'].removesuffix('/') + '/')
    statistic_service = StatisticsService(CONF['data_dir_path'].removesuffix('/') + '/')
    chatbot_service = ChatbotService(extractor_service=text_extractor_service,
                                     request_service=request_service,
                                     file_extractor_service=file_extractor_service,
                                     model_service=model_service,
                                     statistics_service=statistic_service
                                     )

    # Checks arguments
    text_extractor_service.extract_words(input)
    is_precondition_valid, error_msg = chatbot_service.verify_number_arguments()
    if not is_precondition_valid:
        return error_msg
    can_request_be_computed = chatbot_service.check_requests()
    if not can_request_be_computed[0]:
        return request_service.get_general_formatted_request_message()
    # get parquet file name
    chatbot_service.find_valid_parquets()
    # checks beforehand whether there are still requests to compute to avoid wasting time
    if not request_service.get_all_requests():
        return request_service.get_general_request_message()

    # split des mots à faire plus évolué par la suite
    request_input = input.replace("'", " ")  # cas de l'écart-type

    # identification du temps lié à la demande
    # à généraliser si plusieurs requêtes peuvent être faites dans une seule demande
    tense = model_service.identify_tense(request_input)
    # Analyse à faire pour les temps couverts sinon réponse que pas possible
    chatbot_service.compute_data(tense, request_input)

    # if tense == "present":
    #     answer = {"type_message": OutputType.TEXT,
    #               "message": "Je ne suis actuellement pas en mesure de donner la valeur actuelle des capteurs en temps réel."}
    # elif tense == "future":
    #     answer = make_prediction(words)
    # elif tense == "past":
    #     answer = make_statistic(words)
    # else:
    #     answer = "Je n'ai pas compris votre demande."
    return request_service.get_general_formatted_request_message()


x = chatbotv0("Quel était le co2 dans la salle Turing au cours des mois ?")

# plt.show(x[1])
# print(type(x[1]))
print(x)
# img = mpimg.imread(x[1])

# display the image using matplotlib's imshow function

# plt.imshow(img)

# show the plot
# plt.show()
# stagiaire front-end:
# accès aux bds
# rafraichissement bds


# Back-up on gitlab:
# git checkout -b master
# git commit -m "commit 0.6"
# git pull origin master (needed?)
# git push origin master
# see https://mascor.fh-aachen.de/python/gitlab.html


# git add data_cco_od_building_20210101_20230802


# dict = {"type_response": "1", "message": "hello les petits gars"}
#
# print(dict)

from NLP.domain.model.enum.entity_enum import MetricMappingEnum, TimeMappingEnum
from NLP.domain.model.enum.keywords_enum import StatisticEnum
from NLP.domain.model.enum.message_type_enum import OutputType, AnswerMessage, ErrorMessage
from NLP.domain.model.enum.model_enum import TimeEnum
from NLP.domain.model.request_details import RequestDetails


class StatisticsService:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.sensor_file_extension = '_0.parquet.gzip'
        self.separator = '_'

    def access_to_data(self, parquet_file: str):
        """
        accès aux données
        une source actuellement, multisource après

        :param parquet_file:
        :return:
        """
        import pandas as pd

        series = pd.read_parquet(self.data_path + parquet_file + self.sensor_file_extension)
        values = [i[0] for i in series.values.tolist()]
        df = pd.DataFrame({"date": series.index.tolist(), "values": values})
        df['date'] = pd.to_datetime(df['date'], unit="s")
        df["dates"] = df["date"].dt.date
        df["times"] = df["date"].dt.time

        # dataframe is returned because time series leads to errors when making computations on date times indexes
        return df

    def make_statistic(self, request: RequestDetails, period: TimeEnum, number_for_period: int):
        import pandas as pd
        from dateutil.relativedelta import relativedelta

        ts_part = pd.DataFrame(
            columns=['A', 'B', 'C'])  # ts_part va contenir la série de données par après, first random names

        # si changement dans ce dictionaire, changer aussi sa redéfinition à la fin de la fonction
        statistics = {"mode": ts_part.iloc[:, 1].mode(), "moyenne": ts_part.iloc[:, 1].mean(),
                      "médiane": ts_part.iloc[:, 1].median(), "variance": ts_part.iloc[:, 1].var(),
                      "écart-type": ts_part.iloc[:, 1].std()}
        print(request.statistic)
        if not request.statistic:
            statistics_list = ', '.join(statistics.keys())
            return {"type_message": OutputType.ERROR,
                    "message": f"{ErrorMessage.STATISTIC_UNK.value.format(statistics_list)}".removesuffix('.') + '.'
                    }

        ts = self.access_to_data(request.parquets[0])
        if period == TimeEnum.ALL:
            ts_part = ts
        else:
            delta_time = 0
            to_exec = "delta_time = relativedelta({}={})".format(period.value, number_for_period)
            exec(to_exec)
            match period:
                case TimeEnum.YEARS:
                    delta_time = relativedelta(years=number_for_period)
                case TimeEnum.MONTHS:
                    delta_time = relativedelta(months=number_for_period)
                case TimeEnum.DAYS:
                    delta_time = relativedelta(days=number_for_period)

            # FIXME: Retrieve current data when refreshing the datasets is feasible.
            start_date = max(ts.date) - delta_time
            ts_part = ts[ts["date"] >= start_date]

        statistics = {"mode": ts_part.iloc[:, 1].mode(),
                      StatisticEnum.MEAN: ts_part.iloc[:, 1].mean(),
                      StatisticEnum.MEDIAN: ts_part.iloc[:, 1].median(),
                      StatisticEnum.VARIANCE: ts_part.iloc[:, 1].var(),
                      StatisticEnum.STANDARD_DEVIATION: ts_part.iloc[:, 1].std()
                      }
        metric = request.parquets[0].split(self.separator)[-1]
        return {"type_message": OutputType.TEXT,
                "message": AnswerMessage[request.statistic.name].value.format(request.measure.value[-1],
                                                                              request.room.value[-1],
                                                                              statistics.get(request.statistic),
                                                                              MetricMappingEnum[metric.upper()].value
                                                                              ).removesuffix('.') + '.',
                }

    def make_prediction(self, request: RequestDetails, period: TimeEnum, number_for_period: int):
        # Accès aux données
        ts = self.access_to_data(request.parquets[0])
        # Analyse
        from dateutil.relativedelta import relativedelta
        # FIXME: for all time, throws an error because when finding start_date, ts_daily?index is a relativedate.
        #  It is the same for make_statistics
        delta_time = 0
        match period:
            case TimeEnum.YEARS:
                delta_time = relativedelta(years=number_for_period)
            case TimeEnum.MONTHS:
                delta_time = relativedelta(months=number_for_period)
            case TimeEnum.DAYS:
                delta_time = relativedelta(days=number_for_period)

        ts_daily = ts[["dates", "values"]].groupby("dates").mean()
        # start_date = max(ts.index) - delta_time
        # FIXME: Retrieve current data when refreshing the datasets is feasible and the max.
        start_date = max(ts_daily.index) - delta_time
        ts_part = ts_daily[ts_daily.index >= start_date]

        # Make ar model
        from statsmodels.tsa.ar_model import AutoReg
        model = AutoReg(ts_part.values, lags=1)
        model_fit = model.fit()
        # make prediction
        yhat = model_fit.predict(len(ts) + number_for_period, len(ts) + number_for_period)
        metric = request.parquets[0].split(self.separator)[-1]
        return {"type_message": OutputType.TEXT,
                "message": 'La valeur prédite de la salle {} dans {} est de {:.6} {} pour dans {} {}.'.format(
                    request.measure.value[-1],
                    request.room.value[-1],
                    yhat[0],
                    MetricMappingEnum[metric.upper()].value,
                    number_for_period,
                    TimeMappingEnum[period.value.upper()].value).removesuffix('.') + '.'
                }

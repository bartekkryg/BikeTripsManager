import pandas as pd
from datetime import datetime
from settings import Settings


class CSVParser:
    """
    Class used for parsing csv to pandas dataframe \n

    Attributes:

    wd: str working directory

    """

    def __init__(self):
        self.wd = Settings.WD

    def read_csv_trip_attributes(self, in_file=''):
        """
        Reads first line from file to get trip name and trip time

        :param str in_file: name of a csv file

        :return:

            str trip_name: name of a trip

            str trip_total_time: total time in H:M:S format

        """
        path = self.wd + '/' + in_file
        trip_attributes = pd.read_csv(path, header=0, nrows=1, skiprows=0, usecols=[5, 6])
        trip_total_time = trip_attributes.iloc[0, 0]
        trip_total_time = datetime.utcfromtimestamp(int(trip_total_time) / 1000).strftime('%H:%M:%S')
        trip_name = trip_attributes.iloc[0, 1]
        return trip_name, trip_total_time

    def read_csv_trip_data(self, in_file=''):
        """
        Reads trip data from file, gps data, speed, altitude, time

        :param str in_file: name of a csv file

        :return: pandas.DataFrame trip_data: parsed data from csv file

        """
        path = self.wd + '/' + in_file
        trip_data = pd.read_csv(path,
                                header=0,
                                skiprows=[1],
                                usecols=range(5),
                                names=['latitude', 'longtitude', 'altitude', 'speed', 'time'],
                                parse_dates=['time'],
                                date_parser=lambda x:
                                datetime.utcfromtimestamp(int(x) / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                                converters={'speed': lambda x: float(x) * 18 / 5})  # convert to km/h
        return trip_data


if __name__ == '__main__':
    parser = CSVParser()
    trip1 = parser.read_csv_trip_data('Wycieczka 28.04.2021.csv')
    print(trip1.head(1).values.tolist())

from database import TripsDB, TripData, TripId
from csv_parser import CSVParser, pd
from trip import Trip


class Manager:
    """
    Manager is an interface connecting database with gui.

    It works like a controller in a typical Model-View-Controller application


    Attributes:

        db : TripsDB object

        Instance of TripsDB. Used to connect with database

        parser : CSVParser object

        Instance of CSVParser. Used to parse csv files

        trips : dict

        Dictionary to hold all trips from database


    Methods:

    """

    def __init__(self):
        self.db = TripsDB()
        self.parser = CSVParser()
        self.trips = {}

    def populate_db(self, filenames):
        """
        Creates tables for database and populates using parsed data from files

        :param list filenames: list of file names

        """
        session = self.db.Session()
        self.db.create_table()
        if session.query(TripId.id).first() is None:
            self.populate_trip_data(filenames)

    def populate_trip_data(self, filenames):
        """
        Parses data and adds to database

        :param filenames: list of file names

        """
        trips = []
        for idx, file in enumerate(filenames):
            file = '/Cycledroid' + '/' + file
            trip_name, trip_total_time = self.parser.read_csv_trip_attributes(file)
            trip_data = self.parser.read_csv_trip_data(file)
            trip_data['trip_id'] = idx + 1
            trips.append(trip_data)
            self.db.add_trip_id(name=trip_name, total_time=trip_total_time)
            print(f"Adding trip {trip_name} - id:{idx + 1}")

        combined_trip_data = pd.concat(trips, ignore_index=True, sort=False)
        combined_trip_data.to_sql(name='TripData', con=self.db.engine, if_exists='append', index_label='id')

    def save_all_trips(self):
        """
        Sets trips property using data from database

        """
        ids = self.read_trip_ids()
        for trip_id in ids:
            if trip_id not in self.trips.keys():
                trip_data = self.read_trip_data(trip_id)
                self.trips[trip_id] = trip_data

    def read_trip_ids(self):
        """
        Reads all trip ids from database

        :return:   pandas.Series trip_ids: series of all trip ids
        """
        session = self.db.Session()
        sql_query = session.query(TripId.id).statement
        with self.db.engine.connect() as connection:
            trip_ids = pd.read_sql(sql_query, connection)

        return trip_ids['id']

    def read_trip_name(self, trip_id):
        """
        Reads trip name from database

        :param int trip_id: trip id

        :return: str trip_name: name of a trip

        """
        session = self.db.Session()
        sql_query = session.query(TripId.name).filter(TripId.id == trip_id).statement
        with self.db.engine.connect() as connection:
            trip_name = pd.read_sql(sql_query, connection)

        return trip_name['name'].item()

    def read_trip_data(self, trip_id):
        """
        Reads trip data from database

        :param int trip_id: trip id

        :return: Trip trip_data: Trip object created from database data

        """
        session = self.db.Session()
        sql_query = session.query(TripData.latitude, TripData.longtitude, TripData.speed, TripData.altitude). \
            filter_by(trip_id=trip_id).statement
        with self.db.engine.connect() as connection:
            trip_data = pd.read_sql(sql_query, connection)

        return Trip(trip_data)

    def get_last_trip_id(self):
        """
        Reads last added trip's id

        :return: int trip id

        """
        session = self.db.Session()
        sql_query = session.query(TripId.id).order_by(TripId.id).statement
        with self.db.engine.connect() as connection:
            trip_id = pd.read_sql(sql_query, connection).tail(1)['id']

        return trip_id

    def insert_trips(self, in_file_stream):
        """
        Adds new trips to database

        :param list in_file_stream: list of file names

        """
        last_trip_id = self.get_last_trip_id()
        trips = []
        for idx, file in enumerate(in_file_stream, 1):
            file = '/Cycledroid' + '/' + file
            trip_name, trip_total_time = self.parser.read_csv_trip_attributes(file)
            trip_data = self.parser.read_csv_trip_data(file)
            trip_data['trip_id'] = idx + int(last_trip_id)
            trips.append(trip_data)
            self.db.add_trip_id(name=trip_name, total_time=trip_total_time)

        combined_trip_data = pd.concat(trips, ignore_index=True, sort=False)
        combined_trip_data.to_sql(name='TripData', con=self.db.engine, if_exists='append', index_label='id',
                                  index=False)

    def delete_rows(self):
        """
        Clears tables

        """
        session = self.db.Session()
        session.query(TripId).delete()
        session.query(TripData).delete()
        session.commit()


if __name__ == '__main__':
    manager = Manager()
    # manager.save_all_trips()
    # manager.trips[5].draw()
    # print(manager.read_trip_names())
    print(manager.read_trip_data(1).geo)

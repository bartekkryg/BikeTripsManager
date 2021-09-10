import unittest
from trip import Trip
from csv_parser import CSVParser
import pandas as pd
import os
from database import TripsDB
import sqlalchemy
from manager import Manager
from settings import Settings


class TestCSVParser(unittest.TestCase):
    def setUp(self):
        self.parser = CSVParser()
        self.test_file = 'Wycieczka 28.04.2021.csv'

    def test_file_exists(self):
        self.assertTrue(os.path.isfile(self.test_file))

    def test_read_trip_attrs(self):
        trip_name = 'Wycieczka 28.04.2021'
        trip_total_time = '01:05:05'

        parsed = self.parser.read_csv_trip_attributes(self.test_file)

        self.assertEqual(trip_name, parsed[0])
        self.assertEqual(trip_total_time, parsed[1])

    def test_read_trip_data(self):
        first_row = [50.670597, 17.967216, 182.5, 1.8103809599999998, pd.Timestamp('2021-04-28 17:12:44')]
        first_row_parsed = self.parser.read_csv_trip_data(self.test_file).head(1).values.tolist()[0]

        self.assertEqual(first_row, first_row_parsed)


class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.test_db = TripsDB(db='sqlite:///trips_test.db')

    def test_create_table(self):
        self.test_db.create_table()
        insp = sqlalchemy.inspect(self.test_db.engine)
        self.assertTrue(insp.has_table('TripId'))
        self.assertTrue(insp.has_table('TripData'))

    def test_drop_table(self):
        self.test_db.create_table()
        insp = sqlalchemy.inspect(self.test_db.engine)
        self.assertTrue(insp.has_table('TripId'))
        self.assertTrue(insp.has_table('TripData'))
        self.test_db.drop_table()
        insp = sqlalchemy.inspect(self.test_db.engine)
        self.assertFalse(insp.has_table('TripId'))
        self.assertFalse(insp.has_table('TripData'))

    def test_check_if_empty(self):
        self.test_db.create_table()
        self.assertTrue(self.test_db.check_if_empty())

    def test_add_trip_id(self):
        self.test_db.drop_table()
        self.test_db.create_table()
        name = 'Wycieczka 28.04.2021'
        total_time = '01:05:05'
        self.assertTrue(self.test_db.check_if_empty())
        self.test_db.add_trip_id(name, total_time)
        self.assertFalse(self.test_db.check_if_empty())

    def tearDown(self):
        self.test_db.drop_table()


class TestManager(unittest.TestCase):

    def setUp(self):
        self.manager = Manager()
        self.manager.db = TripsDB(db='sqlite:///trips_test.db')
        self.manager.db.create_table()
        self.parser = CSVParser()

        trip_data = self.parser.read_csv_trip_data('Wycieczka 28.04.2021.csv')
        name, total_time = self.parser.read_csv_trip_attributes('Wycieczka 28.04.2021.csv')
        self.manager.db.add_trip_id(name, total_time)
        trip_data['trip_id'] = 1
        trip_data.to_sql(name='TripData', con=self.manager.db.engine, if_exists='append', index_label='id')
        self.manager.trips[1] = Trip(trip_data)
        self.test_saved_trips = self.manager.trips.copy()

    def tearDown(self):
        self.manager.db.drop_table()

    def test_get_last_id(self):
        trip_id = 1
        self.assertEqual(trip_id, int(self.manager.get_last_trip_id()))

    def test_insert_trips(self):
        test_file_stream = ['Wycieczka 28.04.2021.csv']
        self.assertEqual(1, int(self.manager.get_last_trip_id()))
        self.manager.insert_trips(test_file_stream)
        self.assertEqual(2, int(self.manager.get_last_trip_id()))

    def test_read_trip_ids(self):
        ids = self.manager.read_trip_ids()
        test_series = pd.Series([1], name='id')
        pd.testing.assert_series_equal(test_series, ids)

    def test_read_trip_name(self):
        name = self.manager.read_trip_name(1)
        test_name = 'Wycieczka 28.04.2021'
        self.assertEqual(test_name, name)

    def test_read_trip_data(self):
        trip_data = self.manager.read_trip_data(1)
        self.assertIsInstance(trip_data, Trip)
        pd.testing.assert_frame_equal(self.manager.trips[1].geo, trip_data.geo)
        pd.testing.assert_series_equal(self.manager.trips[1].speed, trip_data.speed)
        pd.testing.assert_series_equal(self.manager.trips[1].altitude, trip_data.altitude)

    def test_save_all_trips(self):
        self.manager.trips = {}
        self.manager.save_all_trips()
        self.assertEqual(self.test_saved_trips.keys(), self.manager.trips.keys())
        pd.testing.assert_frame_equal(self.test_saved_trips[1].geo, self.manager.trips[1].geo)

    def test_delete_rows(self):
        self.assertFalse(self.manager.db.check_if_empty())
        self.manager.delete_rows()
        self.assertTrue(self.manager.db.check_if_empty())

    def test_populate_trip_data(self):
        self.manager.delete_rows()
        self.manager.populate_trip_data(filenames=Settings.FILES)
        self.assertFalse(self.manager.db.check_if_empty())

    def test_populate_db(self):
        self.manager.db.drop_table()
        self.manager.populate_db(filenames=Settings.FILES)
        self.assertFalse(self.manager.db.check_if_empty())
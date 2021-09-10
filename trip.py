from collections import namedtuple


class Trip:
    """
    Class for storing trip's data. Later used in GUI

    Attributes:

        geo: pandas.DataFrame stores gps data

        speed: pandas.Series stores speed data

        altitude: pandas.Series stores altitude data


    Methods:

    """

    def __init__(self, trip_data):
        # trip_data is a pandas dataframe
        self.geo = trip_data[['latitude', 'longtitude']]
        self.speed = trip_data['speed']
        self.altitude = trip_data['altitude']

    def get_bbox(self):
        """
        Gets boundaries of a box for plotting map

        :return: tuple of 4 gps points
        """
        bbox = namedtuple('bbox', ['lat_min', 'lon_min', 'lat_max', 'lon_max'])
        return bbox(
            self.geo['latitude'].min(), self.geo['longtitude'].min(),
            self.geo['latitude'].max(), self.geo['longtitude'].max()
        )

    def get_pixel_data(self, trip_map):
        """
        Converts gps data to pixel for plotting

        :param trip_map: gps data

        :return: pandas dataframe converted from lat/lon to pixels

        """
        return self.geo.apply(lambda x: trip_map.to_pixels(x), axis=1, result_type='expand')

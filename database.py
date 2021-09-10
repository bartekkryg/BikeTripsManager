from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import Column, Integer, Float, DateTime, Time, String
from datetime import datetime

Base = declarative_base()


class TripId(Base):
    __tablename__ = 'TripId'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    total_time = Column(Time, nullable=False)
    trip = relationship('TripData')


class TripData(Base):
    __tablename__ = 'TripData'
    id = Column(Integer, primary_key=True)
    latitude = Column(Float, nullable=False)
    longtitude = Column(Float, nullable=False)
    altitude = Column(Float, nullable=False)
    speed = Column(Float, nullable=False)
    time = Column(DateTime, nullable=False)
    trip_id = Column(Integer, ForeignKey('TripId.id'))


class TripsDB:
    """
    Interface for connecting with sqlite database. Acts like a Model in a Model-View-Controller application

    Attributes:

        engine: SQLAlchemy engine object

        Session: SQLAlchemy session object

    """

    def __init__(self, db='sqlite:///trips.db'):
        self.engine = create_engine(db, echo=True)
        self.Session = sessionmaker(bind=self.engine)
        self.create_table()

    def create_table(self):
        """
        Creates tables

        """
        Base.metadata.create_all(self.engine.connect(), checkfirst=True)

    def drop_table(self):
        """
        Drops tables

        """
        Base.metadata.drop_all(self.engine.connect(), checkfirst=True)

    def add_trip_id(self, name, total_time):
        """
        Adds trip to database

        :param str name: name of a trip

        :param str total_time: total time of a trip

        """
        sess = self.Session()
        total_time = datetime.strptime(total_time, '%H:%M:%S').time()
        row = TripId(name=name, total_time=total_time)
        sess.add(row)
        sess.commit()

    def check_if_empty(self):
        """
        Checks if TripId table is empty

        :return: bool
        """
        session = self.Session()
        if session.query(TripId.id).first() is None:
            return True
        return False


if __name__ == '__main__':
    db = TripsDB()
    db.create_table()

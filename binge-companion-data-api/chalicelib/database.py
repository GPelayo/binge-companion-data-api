from sqlalchemy import Column, create_engine, Integer, String, text
from sqlalchemy.orm import declarative_base, sessionmaker

from chalicelib.config import RDB_USER, RDB_PASSWORD, RDB_HOST, RDB_DATABASE_NAME

Base = declarative_base()


class Series(Base):
    __tablename__ = "series"

    series_id = Column(Integer, primary_key=True)
    name = Column(String)
    season_count = Column(Integer)
    thumbnail_url = Column(String)

    def __str__(self):
        return self.name


class DatabaseConnection:
    def __init__(self):
        engine = create_engine(f"postgresql://{RDB_USER}:{RDB_PASSWORD}@{RDB_HOST}:5432/{RDB_DATABASE_NAME}")
        self.session_maker = sessionmaker(bind=engine)
        self.session = None
        print('Connecting to Database')
        engine.connect()

    def connect(self):
        self.session = self.session_maker()

    def list_series(self):
        print('Listing Eps')
        print(self.session.bind)

        return {
            'series': [
                {
                    'id': series.series_id,
                    'name': series.name,
                    'season_count': series.season_count
                } for series in self.session.query(Series).all()
            ]
        }

    def get_series(self, series_id):
        series = self.session.get(Series, series_id)

        return {k: str(v) for k, v in series.__dict__.items() if k[0] != '_'}

    def get_episodes_from_season(self, series_id, season):
        episodes = self.session.execute(text("SELECT episode_id, name FROM episode"
                                             f" WHERE episode.series_id = '{series_id}'"
                                             f" AND episode.season = '{season}'")).all()

        return {
            "episodes": [
                {
                    'episode_id': episode_id,
                    'name': name
                 } for episode_id, name in episodes
            ]
        }

    def get_episode(self, episode_id):
        name, series_id, season = self.session.execute(text(f"SELECT name, series_id, season FROM episode"
                                                                f" WHERE episode.episode_id = '{episode_id}'")).one()

        return {
            'episode_id': episode_id,
            'name': name,
            'series_id': series_id,
            'season': season
        }

    def get_trivia_from_episode(self, episode_id):
        trivia = self.session.execute(text(f"SELECT text FROM trivia WHERE trivia.episode_id = '{episode_id}'")).all()

        return {
            "trivia": [i[0] for i in trivia]
        }

    def __enter__(self):
        self.session = self.session_maker()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

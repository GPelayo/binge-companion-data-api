from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from binge_models.models import Series

from chalicelib.config import RDB_USER, RDB_PASSWORD, RDB_HOST, RDB_DATABASE_NAME


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

    def get_episodes_from_series(self, series_id, season=None):
        query = f"SELECT episode_id, name FROM episode WHERE episode.series_id = '{series_id}'"

        if season:
            query += f" AND episode.season = '{season}'"

        episodes = self.session.execute(text(query)).all()

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

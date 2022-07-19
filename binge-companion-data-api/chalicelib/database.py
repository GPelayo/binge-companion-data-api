from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from binge_models.models import Series

from chalicelib.config import RDB_USER, RDB_PASSWORD, RDB_HOST, RDB_DATABASE_NAME


class BingeDatabase:
    def __init__(self):
        engine = create_engine(f"postgresql://{RDB_USER}:{RDB_PASSWORD}@{RDB_HOST}:5432/{RDB_DATABASE_NAME}")
        self.session_maker = sessionmaker(bind=engine)
        self.session = None
        engine.connect()

    def connect(self):
        self.session = self.session_maker()

    def list_object(self, model, list_name=None, filters=None):
        list_name = list_name or model.__tablename__
        filters = [] if filters is None else filters
        obj_list = self.session.query(model).filter(*filters).all()
        fields = [columns.name for columns in model.__table__.columns]

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

    def list_episode_names(self, series_id, season=None):
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

    def list_trivia_text_from_episode(self, episode_id):
        trivia = self.session.execute(text(f"SELECT text FROM trivia WHERE trivia.episode_id = '{episode_id}'")).all()

        return {
            "trivia": [i[0] for i in trivia]
        }

    def __enter__(self):
        self.session = self.session_maker()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

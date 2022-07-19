from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from binge_models.models import Series, Episode, Trivia

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
            list_name: [
                {field: getattr(obj, field) for field in fields} for obj in obj_list
            ]
        }

    def list_series(self):
        return self.list_object(Series)

    def get_series(self, series_id):
        series = self.session.get(Series, series_id)

        return {k: str(v) for k, v in series.__dict__.items() if k[0] != '_'}

    def list_episode(self, series_id, season=None):
        filters = [Episode.series_id == series_id] + [Episode.season == season] if season else []

        return self.list_object(Episode, list_name='episodes', filters=filters)

    def get_episode(self, episode_id):
        episode = self.session.get(Episode, episode_id)

        return {k: str(v) for k, v in episode.__dict__.items() if k[0] != '_'}

    def list_trivia(self, episode_id):
        return self.list_object(Trivia, filters=[Trivia.episode_id == episode_id])

    def __enter__(self):
        self.session = self.session_maker()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

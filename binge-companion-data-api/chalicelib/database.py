from typing import Any, AnyStr, Dict, List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from binge_models.models import Base, Series, Episode, Trivia

from chalicelib.config import RDB_USER, RDB_PASSWORD, RDB_HOST, RDB_DATABASE_NAME


class BingeDatabase:
    def __init__(self):
        engine = create_engine(f"postgresql://{RDB_USER}:{RDB_PASSWORD}@{RDB_HOST}:5432/{RDB_DATABASE_NAME}")
        self.session_maker = sessionmaker(bind=engine)
        self.session = None
        engine.connect()

    def list_object(self, model: Base, list_name: AnyStr = None, filters: List[bool] = None) -> Dict[AnyStr, List]:
        list_name = list_name or model.__tablename__
        filters = [] if filters is None else filters
        obj_list = self.session.query(model).filter(*filters).all()
        fields = [columns.name for columns in model.__table__.columns]

        return {
            list_name: [
                {field: getattr(obj, field) for field in fields} for obj in obj_list
            ]
        }

    def list_series(self) -> Dict[AnyStr, List]:
        return self.list_object(Series)

    def get_series(self, series_id: AnyStr) -> Dict[AnyStr, List]:
        series = self.session.get(Series, series_id)

        return {k: str(v) for k, v in series.__dict__.items() if k[0] != '_'}

    def list_episode(self, series_id: AnyStr, season: AnyStr = None) -> Dict[AnyStr, List]:
        filters = [Episode.series_id == series_id] + [Episode.season == season] if season else []

        return self.list_object(Episode, list_name='episodes', filters=filters)

    def get_episode(self, episode_id: AnyStr) -> Dict[AnyStr, List]:
        episode = self.session.get(Episode, episode_id)

        return {k: str(v) for k, v in episode.__dict__.items() if k[0] != '_'}

    def list_trivia(self, episode_id: AnyStr) -> Dict[AnyStr, List]:
        return self.list_object(Trivia, filters=[Trivia.episode_id == episode_id])

    def __enter__(self) -> 'BingeDatabase':
        self.session = self.session_maker()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):
        self.session.close()

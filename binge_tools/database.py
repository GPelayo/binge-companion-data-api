from typing import List
import logging

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, text
from sqlalchemy.orm import declarative_base, sessionmaker

from config import RDB_USER, RDB_PASSWORD, RDB_HOST, RDB_DATABASE_NAME
from scraper import Series


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


Base = declarative_base()


class SQLSeries(Base):
    __tablename__ = "series"

    series_id = Column(String, primary_key=True)
    name = Column(String)
    season_count = Column(Integer)
    thumbnail_url = Column(String)

    def __init__(self, series_id: str, name: str):
        self.series_id = series_id
        self.name = name
        self.season_count = -1
        self.thumbnail_url = None
        self.episodes = []
        self.series_wide_trivia = []


class SQLEpisode(Base):
    __tablename__ = "episode"

    episode_id = Column(String, primary_key=True)
    name = Column(String)
    season = Column(Integer)
    series_id = Column(String, ForeignKey('series.series_id'))

    def __init__(self, episode_id: str, name: str, season: int, series_id: str):
        self.episode_id = episode_id
        self.name = name
        self.season = season
        self.series_id = series_id


class SQLTrivia(Base):
    __tablename__ = "trivia"

    trivia_id = Column(String, primary_key=True)
    episode_id = Column(String, ForeignKey('episode.episode_id'))
    series_id = Column(String, ForeignKey('series.series_id'))
    score = Column(Integer)
    score_denominator = Column(Integer)
    text = Column(String)

    def __init__(self, trivia_id: str, text: str, series_id: str, episode_id: str = None):
        self.trivia_id = trivia_id
        self.score = -1
        self.score_denominator = -1
        self.text = text
        self.series_id = series_id
        self.episode_id = episode_id


class TriviaTag(Base):
    __tablename__ = "trivia_tag"

    trivia_tag_id = Column(Integer, primary_key=True)
    trivia_id = Column(String, ForeignKey('trivia.trivia_id'))
    text = Column(String)

    def __init__(self, trivia_id: str, text: str):
        self.trivia_id = trivia_id
        self.text = text


class DatabaseConnection:
    def __init__(self):
        engine = create_engine(f"postgresql://{RDB_USER}:{RDB_PASSWORD}@{RDB_HOST}:5432/{RDB_DATABASE_NAME}")
        self.session_maker = sessionmaker(bind=engine)
        self.session = self.session_maker()

    def has_series(self, series_id):
        series = self.session.execute(text(f"SELECT 1 FROM series WHERE '{series_id}' = series.series_id"))
        return series is None

    def write_series(self, series: Series):
        # TODO add proper update checks
        sql_series = self.session.get(SQLSeries, series.series_id)
        trivia_batch = {}
        episode_batch = {}
        if sql_series:
            old_episodes = self.session.query(SQLEpisode).filter(SQLEpisode.series_id == series.series_id)
            episode_batch = {oe.episode_id: oe for oe in old_episodes}

            for t in self.session.query(SQLTrivia).filter(SQLTrivia.series_id == series.series_id).all():
                trivia_batch[t.trivia_id] = t
        else:
            sql_series = SQLSeries(series_id=series.series_id, name=series.name)
            self.session.add(sql_series)
            self.session.commit()

        for k, v in series.__dict__.items():
            if not isinstance(v, List):
                setattr(sql_series, k, v)

        for st in series.series_wide_trivia:
            if st.trivia_id not in trivia_batch:
                trivia_batch[st.trivia_id] = SQLTrivia(st.trivia_id, st.text, series.series_id)

        for e in series.episodes:
            if e.episode_id in episode_batch:
                sqle = episode_batch[e.episode_id]
            else:
                sqle = SQLEpisode(e.episode_id, e.name, e.season, sql_series.series_id)

            for k, v in e.__dict__.items():
                if not isinstance(v, List):
                    setattr(sqle, k, v)
            for et in e.trivia:
                print(et.text)
                if et.trivia_id not in trivia_batch or not trivia_batch[et.trivia_id].episode_id:
                    trivia_batch[et.trivia_id] = SQLTrivia(et.trivia_id, et.text, series.series_id, e.episode_id)
                else:
                    logger.log(logging.WARNING, f'Skipping Duplicate {et.trivia_id}.')

            self.session.add(sqle)
        for t in trivia_batch.values():
            print('$', t.trivia_id, t.text)
            if t.text:
                self.session.add(t)
        self.session.commit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

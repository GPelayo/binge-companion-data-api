import json
import sys

from binge_models.models import Series, Episode, Trivia, TriviaTag
from chalice.test import Client
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import dotenv

from app import app
from chalicelib import config

dotenv.load_dotenv()
this_module = sys.modules[__name__]


class ExpectedOutputs:
    def __init__(self):
        with open('dummy_data.json', 'r') as tf:
            test_series = json.load(tf)

            self.series_endpoint = {
                'series': [{
                    'id': series['series_id'],
                    'name': series['name'],
                    'season_count': series['season_count']
                } for series in test_series['series']]
            }

            for series in test_series['series']:
                if series['series_id'] == '1110':
                    test_season_1_episodes = series['episodes']
                    self.season_1_episodes = {
                        'episodes': [{
                            'episode_id': test_episode['episode_id'],
                            'name': test_episode['name']
                        } for test_episode in test_season_1_episodes if test_episode['season'] == 1]
                    }
                    for ep in series['episodes']:
                        if ep['episode_id'] == '2.1':
                            self.episode_2_1_trivia = {'trivia': [trivia['text'] for trivia in ep['trivia']]}
                            break
                    break


class TestDatabase:
    test_series = None
    engine = create_engine(f"postgresql://{config.RDB_USER}:"
                           f"{config.RDB_PASSWORD}@{config.RDB_HOST}:5432/{config.RDB_DATABASE_NAME}")

    def _cleanup(self):
        session = sessionmaker(bind=self.engine)()
        for m in [TriviaTag, Trivia, Episode, Series]:
            m.__table__.drop(bind=self.engine)
        session.close()
        self.engine.dispose()

    def _build_database(self):
        for m in [Series, Episode, Trivia, TriviaTag]:
            m.__table__.create(bind=self.engine)

        with open('dummy_data.json', 'r') as tf:
            dummy_data = json.load(tf)
            dummy_series_list = []
            dummy_episode_list = []
            dummy_trivia_map = {}

            for series in dummy_data['series']:
                dummy_series = Series(series['series_id'], series['name'])
                dummy_series.season_count = series['season_count']
                for episode in series['episodes']:
                    dummy_episode = Episode(episode['episode_id'],
                                            episode['name'],
                                            episode['season'],
                                            dummy_series.series_id)
                    # TODO add trivia field in Episode from model repo
                    for episode_trivia in episode['trivia']:
                        dummy_trivia = Trivia(episode_trivia['trivia_id'],
                                              episode_trivia['text'],
                                              dummy_series.series_id,
                                              dummy_episode.episode_id)
                        dummy_trivia_map[dummy_trivia.trivia_id] = dummy_trivia
                    dummy_episode_list.append(dummy_episode)
                dummy_series_list.append(dummy_series)

            for series_trivia in series['series_wide_trivia']:
                if series_trivia['trivia_id'] not in dummy_trivia_map:
                    dummy_trivia = Trivia(series_trivia['trivia_id'],
                                          series_trivia['text'],
                                          dummy_series.series_id)

                dummy_trivia_map[dummy_trivia.trivia_id] = dummy_trivia

            session = sessionmaker(bind=self.engine)()
            session.add_all(dummy_series_list)
            session.commit()
            session.add_all(dummy_episode_list)
            session.commit()
            session.add_all(dummy_trivia_map.values())
            session.commit()
            session.close()

    def __enter__(self):
        self._build_database()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cleanup()


expected_outputs = ExpectedOutputs()


def test_series_view():
    with TestDatabase():
        with Client(app) as client:
            response = client.http.get('/v1/series')
            assert response.json_body == expected_outputs.series_endpoint


def test_episode_view():
    with TestDatabase():
        with Client(app) as client:
            response = client.http.get('/v1/episode?series-id=1110&season=1')
            assert response.json_body == expected_outputs.season_1_episodes


def test_trivia_view():
    with TestDatabase():
        with Client(app) as client:
            response = client.http.get('/v1/trivia?episode-id=2.1')
            assert response.json_body == expected_outputs.episode_2_1_trivia

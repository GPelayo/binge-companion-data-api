from binge_models.models import Series, Episode, Trivia, TriviaTag
from chalice.test import Client
import dotenv
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import app
from chalicelib import config

dotenv.load_dotenv()

test_series = {
            "series": [
                {
                    "series_id": "BS",
                    "name": "The Big Betrayal",
                    "season_count": 2,
                    "thumbnail_url": "http://127.0.0.1:8000",
                    "series_wide_trivia": [
                        {
                            "trivia_id": "big-betrayal",
                            "score": 10,
                            "score_denominator": 10,
                            "text": "Big Setup is big."
                        },
                        {
                            "trivia_id": "big-money",
                            "score": 7,
                            "score_denominator": 10,
                            "text": "Bad guys get big money"
                        }
                    ],
                    "episodes": [
                        {
                            "episode_id": "BB1.1",
                            "name": "Pilot",
                            "season": 1,
                            "trivia": [
                                {
                                    "trivia_id": "IMAX",
                                    "score": 1,
                                    "score_denominator": 121,
                                    "text": "First episode was filmed using IMAX cameras. Changes"
                                },
                                {
                                    "trivia_id": "IRL-Big-Betrayal",
                                    "score": 80,
                                    "score_denominator": 121,
                                    "text": "Series cancelled after executive producer ran off with the funding."
                                }
                            ]
                        },
                        {
                            "episode_id": "BB2.1",
                            "name": "Pilot 2",
                            "season": 2,
                            "trivia": [
                                {
                                    "trivia_id": "Big-Reveal ",
                                    "score": 80,
                                    "score_denominator": 121,
                                    "text": "Series planning to be revived."
                                }
                            ]
                        }
                    ]
                },
                {
                    "series_id": "1110",
                    "name": "Man staring at wall.",
                    "season_count": 2,
                    "series_wide_trivia": [
                        {
                            "trivia_id": "acab",
                            "score": 10,
                            "score_denominator": 10,
                            "text": "Original concept was 'Man watching paint dry'"
                        },
                        {
                            "trivia_id": "1232",
                            "score": 7,
                            "score_denominator": 10,
                            "text": "Season 2 casted a moth. But was cut due to budget reasons."
                        }
                    ],
                    "episodes": [
                        {
                            "episode_id": "1.1",
                            "name": "Pilot",
                            "season": 1,
                            "trivia": [
                                {
                                    "trivia_id": "3",
                                    "score": 1,
                                    "score_denominator": 121,
                                    "text": "Walls suck."
                                },
                                {
                                    "trivia_id": "5",
                                    "score": 80,
                                    "score_denominator": 121,
                                    "text": "Took 5 hours to remove graffiti for filming."
                                }
                            ]
                        },
                        {
                            "episode_id": "1.2",
                            "name": "Shed Wall",
                            "season": 1,
                            "trivia": [
                                {
                                    "trivia_id": "32",
                                    "score": 5,
                                    "score_denominator": 521,
                                    "text": "Walls still suck."
                                },
                                {
                                    "trivia_id": "15",
                                    "score": 89,
                                    "score_denominator": 151,
                                    "text": "Had to cancel rest of the season due to budget restraints."
                                },
                                {
                                    "trivia_id": "89",
                                    "score": 80,
                                    "score_denominator": 121,
                                    "text": "Actor playing 'Man' was request double on his contract. Was planned to be re-casted before the season was canceled."
                                }
                            ]
                        },
                        {
                            "episode_id": "2.1",
                            "name": "Pilot",
                            "season": 2,
                            "trivia": [
                                {
                                    "trivia_id": "1232",
                                    "score": 7,
                                    "score_denominator": 10,
                                    "text": "Season 2 casted a moth. But was cut due to budget reasons."
                                }
                            ]
                        }
                    ]
                }
            ]
        }


@pytest.fixture()
def series_endpoint_result():
    return {
        'series': [{
            'id': series['series_id'],
            'name': series['name'],
            'season_count': series['season_count']
        } for series in test_series['series']]
    }


@pytest.fixture()
def season_1_episodes_result():
    for series in test_series['series']:
        if series['series_id'] == '1110':
            test_season_1_episodes = series['episodes']
            return {
                'episodes': [{
                    'episode_id': test_episode['episode_id'],
                    'name': test_episode['name']
                } for test_episode in test_season_1_episodes if test_episode['season'] == 1]
            }


@pytest.fixture()
def episode_2_1_trivia_result():
    for series in test_series['series']:
        if series['series_id'] == '1110':
            for ep in series['episodes']:
                if ep['episode_id'] == '2.1':
                    return {'trivia': [trivia['text'] for trivia in ep['trivia']]}


@pytest.fixture(scope='function')
def setup_database(request):
    engine = create_engine(f"postgresql://{config.RDB_USER}:"
                           f"{config.RDB_PASSWORD}@{config.RDB_HOST}:5432/{config.RDB_DATABASE_NAME}")

    def cleanup():
        cleanup_session = sessionmaker(bind=engine)()
        for m in [TriviaTag, Trivia, Episode, Series]:
            m.__table__.drop(bind=engine)
        cleanup_session.close()
        engine.dispose()

    request.addfinalizer(cleanup)

    for m in [Series, Episode, Trivia, TriviaTag]:
        m.__table__.create(bind=engine)

    dummy_data = test_series
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

    session = sessionmaker(bind=engine)()
    session.add_all(dummy_series_list)
    session.commit()
    session.add_all(dummy_episode_list)
    session.commit()
    session.add_all(dummy_trivia_map.values())
    session.commit()
    session.close()


def test_series_view(setup_database, series_endpoint_result):
    with Client(app) as client:
        response = client.http.get('/v1/series')
        assert response.json_body == series_endpoint_result


def test_episode_view(setup_database, season_1_episodes_result):
    with Client(app) as client:
        response = client.http.get('/v1/episode?series-id=1110&season=1')
        assert response.json_body == season_1_episodes_result


def test_trivia_view(setup_database, episode_2_1_trivia_result):
    with Client(app) as client:
        response = client.http.get('/v1/trivia?episode-id=2.1')
        assert response.json_body == episode_2_1_trivia_result

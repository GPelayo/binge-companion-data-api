from typing import AnyStr, Dict

from chalice import BadRequestError, Chalice
from chalicelib.database import BingeDatabase

app = Chalice(app_name='binge-companion-api')


@app.route('/v1/series')
def list_series() -> Dict:
    with BingeDatabase() as db:
        return db.list_series()


@app.route('/v1/series/{series_id}')
def get_series(series_id: AnyStr) -> Dict:
    with BingeDatabase() as db:
        return db.get_series(series_id)


@app.route('/v1/episode')
def list_episodes() -> Dict:
    if not (params := app.current_request.query_params):
        raise BadRequestError('No series-id given.')

    series_id = params.get('series-id')
    season = params.get('season')

    if series_id:
        with BingeDatabase() as db:
            return db.list_episode(series_id, season=season)
    else:
        raise BadRequestError('No series-id given.')


@app.route('/v1/episode/{episode_id}')
def get_episode(episode_id: AnyStr) -> Dict:

    with BingeDatabase() as db:
        return db.get_episode(episode_id)


@app.route('/v1/trivia')
def list_trivia() -> Dict:
    episode_id = app.current_request.query_params.get('episode-id')

    if episode_id:
        with BingeDatabase() as db:
            return db.list_trivia(episode_id)

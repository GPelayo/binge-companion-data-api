from chalice import Chalice
from database import DatabaseConnection
from chalice import BadRequestError

app = Chalice(app_name='binge-companion-api')


@app.route('/v1/series')
def series_view():
    with DatabaseConnection() as db:
        return db.list_series()


@app.route('/v1/episode')
def episodes_view():
    series_id = app.current_request.query_params.get('series-id')
    season = app.current_request.query_params.get('season')

    if season and series_id:
        with DatabaseConnection() as db:
            return db.get_episodes_from_season(series_id, season=season)
    else:
        raise BadRequestError


@app.route('/v1/trivia')
def trivia_view():
    episode_id = app.current_request.query_params.get('episode-id')

    if episode_id:
        with DatabaseConnection() as db:
            return db.get_trivia_from_episode(episode_id)

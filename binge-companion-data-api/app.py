from chalice import BadRequestError, Chalice
from chalicelib.database import BingeDatabase

app = Chalice(app_name='binge-companion-api')


@app.route('/v1/series')
def series_view():
    with BingeDatabase() as db:
        return db.list_series()


@app.route('/v1/series/{series_id}')
def get_series(series_id):
    with BingeDatabase() as db:
        return db.get_series(series_id)


@app.route('/v1/episode')
def episodes_view():
    series_id = app.current_request.query_params.get('series-id')
    season = app.current_request.query_params.get('season')

    if series_id:
        with BingeDatabase() as db:
            return db.list_episode(series_id, season=season)
    else:
        raise BadRequestError


@app.route('/v1/episode/{episode_id}')
def get_episode(episode_id):

    with BingeDatabase() as db:
        return db.get_episode(episode_id)


@app.route('/v1/trivia')
def trivia_view():
    episode_id = app.current_request.query_params.get('episode-id')

    if episode_id:
        with BingeDatabase() as db:
            return db.list_trivia(episode_id)

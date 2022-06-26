import json
from typing import List


class BingeObject:
    def serialize(self, as_dict=False) -> str:
        serial_dict = {}
        for k, v in self.__dict__.items():
            if isinstance(v, list) and len(v) > 0 and isinstance(v[0], BingeObject):
                serial_dict[k] = list(map(lambda x: x.serialize(as_dict=True), v))
            else:
                serial_dict[k] = v

        return serial_dict if as_dict else json.dumps(serial_dict)


class Trivia(BingeObject):
    def __init__(self, trivia_id: str, text: str):
        self.trivia_id = trivia_id
        self.score = -1
        self.score_denominator = -1
        self.text = text
        self.tag = []


class Episode(BingeObject):
    def __init__(self, episode_id, name: str, season: int):
        self.episode_id = episode_id
        self.name = name
        self.season = season
        self.trivia = []


class Series(BingeObject):
    def __init__(self, series_id: str, name: str):
        self.series_id = series_id
        self.name = name
        self.season_count = -1
        self.thumbnail_url = None
        self.episodes = []
        self.series_wide_trivia = []

    def get_episodes_from_season(self, season: int) -> List[Episode]:
        return list(filter(lambda x: x.season == season, self.episodes))

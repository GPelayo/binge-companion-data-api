import hashlib
import logging
import re
from typing import List, Tuple
from urllib.parse import urlencode, urlparse, urlunparse

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from exceptions import NoResultsException
from models import Series, Episode, Trivia
from webdriver import ChromeWebDriverFactory


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())


class IMDBSeleniumScraper:
    def __init__(self, will_get_trivia: bool = True):
        self.browser = None
        self.will_get_trivia = will_get_trivia

    def __enter__(self):
        self.browser = ChromeWebDriverFactory().get_webdriver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.browser.close()

    def open_browser(self, browser: WebDriver = None):
        self.browser = browser or ChromeWebDriverFactory().get_webdriver()

    def search_media(self, title: str) -> Tuple[Series, str]:
        log.info(f'Searching for {title} in IMDB...')
        url_pieces = list(urlparse('http://www.imdb.com/find'))
        url_pieces[4] = urlencode({'q': title})
        url = urlunparse(url_pieces)
        self.browser.get(url)

        try:
            title_div = self.browser.find_element(By.XPATH, '//div[@class="findSection"]/h3/a[@name="tt"]/../..')
        except NoSuchElementException:
            raise NoResultsException(f'{title} has no results in IMDB')

        show_result_element = title_div.find_elements(By.XPATH, '//tr/td[@class="result_text"]/a')[0]
        show_url = show_result_element.get_attribute('href')
        series_id = re.findall(r'(?<=title/)tt.+(?=/\?ref)', show_url)[0]

        series = Series(series_id, show_result_element.text)
        if 'title/tt' in show_url:
            thumb_links = show_result_element.find_elements(By.XPATH, '../..//td[@class="primary_photo"]/a/img')
            series.thumbnail_url = thumb_links[0].get_attribute('src') if thumb_links else None

        log.info(f'Found {series.name}. Scraping series...')
        return series, show_url

    def scrape_series_page(self, series, show_url):
        season_link = f'http://www.imdb.com/title/{series.series_id}/episodes'
        series.series_wide_trivia += self.extract_trivia_page(f'https://www.imdb.com/title/{series.series_id}/trivia')
        self.browser.get(season_link)
        series.season_count = len(self.browser.find_elements(By.XPATH, '//select[@id="bySeason"]/option'))
        for season in range(1, series.season_count+1):
            self.browser.get(season_link + f'?season={season}')
            log.info(f'Scraping Season {season}')
            for ep_element in self.browser.find_elements(By.XPATH, '//strong/a[@itemprop="name"]'):
                ep_url = ep_element.get_attribute('href')
                ep_id = re.findall(r'(?<=title/)tt.+(?=/\?ref)', ep_url)[0]
                new_ep = Episode(ep_id, ep_element.text, season)
                series.episodes.append(new_ep)
            for e in series.episodes:
                log.info(f'Scraping Trivia for Episode: {e.name}')
                ep_trivia = self.extract_trivia_page(f'https://www.imdb.com/title/{e.episode_id}/trivia')
                e.trivia = ep_trivia
        return series

    def extract_trivia_page(self, url: str) -> List[Trivia]:
        trivia_set = []
        self.browser.get(url)
        trivia_divs = self.browser.find_elements(By.XPATH, '//div[contains(@id,"tr")]/div[@class="sodatext"]')
        for trivia_div in trivia_divs:
            trivia_id = hashlib.md5((trivia_div.text+url).encode('utf-8')).hexdigest()
            tr = Trivia(trivia_id, trivia_div.text)
            score_div = trivia_div.find_element(By.XPATH, '../div[@class="did-you-know-actions"]/a')
            score_str = re.findall('^[0-9]+', score_div.text)
            if score_str:
                tr.score = int(score_str[0]) if int(score_str[0]) > 0 else 1
                tr.score_denominator = int(re.findall('(?<=of )[0-9]+', score_div.text)[0])
            tr.score_denominator, tr.score = tr.score_denominator, tr.score if tr.score_denominator > 0 else (0, 1)
            trivia_set.append(tr)
        return trivia_set

    def close_browser(self):
        self.browser.close()


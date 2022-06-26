import argparse
import sys

from database import DatabaseConnection
from scraper import IMDBSeleniumScraper


parser = argparse.ArgumentParser('Extracts TV Show data to AWS RDB.')
parser.add_argument('show_title', help='TV Show title for scraping.')
args = parser.parse_args(sys.argv[1:])

if args.show_title:
    with IMDBSeleniumScraper() as scraper:
        series = scraper.search_media(args.show_title)

    with DatabaseConnection() as dc:
        dc.write_series(series)

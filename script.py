import csv
import logging
import argparse
from time import strptime
from urllib.parse import urljoin
from os.path import dirname, basename

import requests
from bs4 import BeautifulSoup

CONTENT = None
INIT_URL = 'https://www.eia.gov/dnav/ng/hist/rngwhhdm.htm'

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('[%(asctime)s] %(message)s'))
logger.addHandler(handler)


def get_params():
    global INIT_URL
    parser = argparse.ArgumentParser()
    parser.add_argument('-url', default=INIT_URL, help='URL to crawl.')
    parser.add_argument('-prefix', default=str(), help='prefix for csv file.')
    args = parser.parse_args()

    INIT_URL = args.url if INIT_URL != args.url else INIT_URL
    if not args.prefix.endswith(('_', '-')):
        args.prefix += '_'
    return args


def get_urls():
    global INIT_URL, CONTENT
    logger.info('Fetching from URL: %s', INIT_URL)
    res = requests.get(INIT_URL)
    bsObj = BeautifulSoup(res.content, features='html.parser')
    CONTENT = bsObj
    return {
        anchor.text.strip().lower(): urljoin(
            dirname(INIT_URL) + '/', anchor.get('href'))
        for anchor in bsObj.select('td.F a.NavChunk')
    }


def handle_variations(urls, params):
    logger.info('Fetched %d variants of data.', len(urls))
    for name, url in urls.items():
        try:
            if name == 'daily':
                data = scrap_daily_data(url)
                write_to_csv(data, params.prefix + 'daily.csv')
            elif name == 'weekly':
                data = scrap_weekly_data(url)
                write_to_csv(data, params.prefix + 'weekly.csv')
            elif name == 'monthly':
                data = scrap_monthly_data(url)
                write_to_csv(data, params.prefix + 'monthly.csv')
            elif name == 'annual':
                data = scrap_annual_data(url)
                write_to_csv(data, params.prefix + 'annual.csv')
        except Exception as exc:
            logging.info('Exception occured while parsing...')
            print(exc)


def get_bsObj(url):
    global INIT_URL, CONTENT
    if basename(url).lower() == basename(INIT_URL).lower():
        logger.info('Using already fetched content of URL: %s', INIT_URL)
        return CONTENT

    logger.info('Fetching from URL: %s', url)
    res = requests.get(url)
    return BeautifulSoup(res.content, features='html.parser')


def write_to_csv(data, filename):
    if not data:
        logger.info('No data to write. Skipping write.')
        return

    logger.info('Writing data to file: %s', filename)
    writer = csv.writer(open(filename, 'w'))
    writer.writerow(['Date', 'Price'])
    writer.writerows(data)


def scrap_daily_data(url):
    data = list()
    bsObj = get_bsObj(url)
    for week in bsObj.select('td.B6'):
        start, end, month, modulus = 0, 0, None, None
        year = week.text.strip().split(' ')[0]
        week_range = [x.strip() for x in week.text.strip().split('to')]

        if len(week_range) >= 2:
            month = week_range[0].split(' ')[1].split('-')[0].strip()
            month = strptime(month, '%b').tm_mon
            start = int(week_range[0].split('-')[-1].strip())
            end = int(week_range[1].split('-')[-1].strip())
        else:
            logger.info('Unexpected week range: %s', week.text)
            continue

        days = week.find_next_siblings('td')
        if start > end:
            offset = len(days) - end - 1
            modulus = start + offset

        for index, day in enumerate(days):
            date = start + index
            if modulus and date > modulus:
                date = date % modulus
                month += 1
            date_string = '%s-%02d-%02d' % (year, month, date)
            value = day.text.strip()
            if value and value != 'NA':
                data.append((date_string, float(value)))
    return data


def scrap_weekly_data(url):
    data = list()
    bsObj = get_bsObj(url)
    for month in bsObj.select('td.B6'):
        year = month.text.strip().split('-')[0]
        value, date_string = float(), str()
        for week in month.find_next_siblings('td'):
            if 'B5' in week['class']:
                date_string = '%s-%s' % (
                    year, week.text.strip().replace('/', '-'))
            if 'B3' in week['class']:
                value = week.text.strip()
            if value and date_string:
                data.append((date_string, float(value)))
                value, date_string = float(), str()
    return data


def scrap_monthly_data(url):
    data = list()
    bsObj = get_bsObj(url)
    for year in bsObj.select('td.B4'):
        for index, month in enumerate(year.find_next_siblings('td')):
            date_string = '%s-%02d' % (year.text.strip(), index + 1)
            value = month.text.strip()
            if value:
                data.append((date_string, float(value)))
    return data


def scrap_annual_data(url):
    data = list()
    bsObj = get_bsObj(url)
    for decade in bsObj.select('td.B4'):
        start = int(decade.text.strip().split("'")[0])
        for index, year in enumerate(decade.find_next_siblings('td')):
            date_string = start + index
            value = year.text.strip()
            if value:
                data.append((date_string, float(value)))
    return data


params = get_params()
urls = get_urls()
handle_variations(urls, params)

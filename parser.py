import time
from datetime import datetime
import logging
import requests
from bs4 import BeautifulSoup



BASE_URL = "https://rg.ru"
NEWS_URL = "https://rg.ru/news.html"

def make_request(url):
    logging.info(f'Request to {url}')
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logging.info(f'Error: {e}')
        return None


def parser():
    logging.info('Start parsing')
    html = make_request(NEWS_URL)
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    items = soup.find_all('li', attrs={'class': 'PageNewsContent_item__NmJXl'})
    logging.info(f'News found: {len(items)}')
    for item in items:
        title = item.find('span', attrs={'class': 'PageNewsContentItem_title___TpWh'})
        if title:
            title = title.text
        else:
            title = 'No title'
        href = item.find('a', attrs={'href': True})['href']
        if href:
            if 'https' in href:
                continue
            else:
                full_url = BASE_URL + href
            logging.info('Parsing article')
            article_data = parse_article(full_url)
            time.sleep(1)
            text = article_data['text'] if article_data['text'] else None
            date = article_data['date'] if article_data['date'] else None

            if date and check_time(date):
                results.append({
                    'title': title,
                    'text': text,
                    'date': date,
                })
            else:
                logging.info(f'News has skipped: {title}')
        else:
            results.append({
                'title': title,
                'text': 'No text',
                'date': 'No date',
            })
    return results


def parse_article(url):
    html = make_request(url)
    soup = BeautifulSoup(html, 'html.parser')
    date = soup.find('div', attrs={'class': 'ContentMetaDefault_date__wS0te'})
    date = date.text if date else None
    text = soup.find('div', attrs={'class': 'PageArticleContent_textWrapper__qjCKN'})
    text = text.text if text else None
    return {'date': date, 'text': text}



def check_time(date: str):
    now = datetime.now()
    date = datetime.strptime(date, '%d.%m.%Y %H:%M')
    return (now - date).total_seconds() <= 86400



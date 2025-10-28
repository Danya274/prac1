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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0'
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
        try:
            href = item.find('a', attrs={'href': True})['href']
        except Exception as e:
            logging.info(f'Error: {e}')
            href = None
        if href:
            if 'https' in href:
                continue
            else:
                full_url = BASE_URL + href
            logging.info('Parsing article')
            try:
                article_data = parse_article(full_url)
                time.sleep(1)
                text = article_data['text'] if article_data['text'] else None
                date = article_data['date'] if article_data['date'] else None
                if date:
                    date = datetime.strptime(date, '%d.%m.%Y %H:%M')
                    results.append({
                        'title': title,
                        'text': text,
                        'link': full_url,
                        'date': date,
                    })
                else:
                    logging.info(f'News has skipped: {title}')
            except Exception as e:
                logging.info(f'Error parse article {full_url}: {e}')
        else:
            results.append({
                'title': title,
                'text': 'No text',
                'link': 'No link',
                'date': 'No date',
            })

    return results


def parse_article(url):
    html = make_request(url)
    soup = BeautifulSoup(html, 'html.parser')
    date = soup.find('div', attrs={'class': 'ContentMetaDefault_date__wS0te'})
    date = date.text if date else None
    if date is None:
        try:
            date_cont = soup.find('div', attrs={'class': 'PageArticle_publishDate__v2Etv'})
            spans = date_cont.find_all('span')
            date_span = spans[0].text.strip()
            time_span = spans[1].text.strip()
            full_date = date_span + ' ' + time_span
            if full_date is None:
                try:
                    date = soup.find('div', attrs={'class': 'PageArticleContentHeader_date__cBz9Q'})
                    date = date.text if date else None
                except Exception as e:
                    logging.error('Error with date parse num2')
        except Exception as e:
            logging.error('Error with date parse num1')
    text = soup.find('div', attrs={'class': 'PageArticleContent_textWrapper__qjCKN'})
    text = text.text if text else None
    if text is None:
        try:
            text = soup.find('div', attrs={'class': 'PageArticleContentStyling_text__iD61m commonArticle_text__ul5uZ'})
            text = text.text if text else None
            if text is None:
                try:
                    text = soup.find('div', attrs={'class': 'PageArticleContentStyling_text__07I2Z commonArticle_text__ul5uZ commonArticle_zoom__SDMjc'})
                    text = text.text if text else None
                except Exception as e:
                    logging.error('Error with text parse num2')
        except Exception as e:
            logging.error('Error with text parse num1')
    remove_share_word = text.rfind('Поделиться') if text else None
    if remove_share_word:
        text = text[:remove_share_word + 1]
    return {'date': date, 'text': text}



# def check_time(date: str):
#     now = datetime.now()
#     date = datetime.strptime(date, '%d.%m.%Y %H:%M')
#     return (now - date).total_seconds() <= 86400

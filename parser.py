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
    if not html:
        logging.error('Failed to fetch news page')
        return []

    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('li', attrs={'class': 'PageNewsContent_item__NmJXl'})
    logging.info(f'News found: {len(items)}')

    results = []
    successful_parses = 0

    for index, item in enumerate(items, 1):
        logging.info(f'Processing article {index}/{len(items)}')

        title_elem = item.find('span', attrs={'class': 'PageNewsContentItem_title___TpWh'})
        if not title_elem:
            logging.debug(f'No title found for item {index}')
            continue

        title = title_elem.get_text(strip=True)
        if not title:
            continue

        href_elem = item.find('a', href=True)
        if not href_elem:
            logging.debug(f'No link found for: {title}')
            continue

        href = href_elem['href']

        if href.startswith('http'):
            logging.debug(f'Skipping external link: {href}')
            continue

        full_url = BASE_URL + href if href.startswith('/') else BASE_URL + '/' + href

        logging.info(f'Parsing article: {title[:50]}...')

        try:
            article_data = parse_article(full_url)
            time.sleep(1)

            text = article_data.get('text')
            date_str = article_data.get('date')

            if not text or not date_str:
                logging.warning(f'Text or date not found for: {full_url}')
                continue

            try:
                date = datetime.strptime(date_str, '%d.%m.%Y %H:%M')
            except ValueError as e:
                logging.error(f'Date parsing error for "{date_str}": {e}')
                continue
            results.append({
                'title': title,
                'text': text,
                'link': full_url,
                'date': date,
            })

            successful_parses += 1
            logging.info(f'Successfully parsed article {successful_parses}')

        except Exception as e:
            logging.error(f'Article parsing error for {full_url}: {e}')
            continue

    logging.info(f'Parsing completed: {successful_parses}/{len(items)} articles successfully parsed')
    return results


def parse_article(url):
    html = make_request(url)
    if not html:
        return {'date': None, 'text': None}
    soup = BeautifulSoup(html, 'html.parser')

    patterns = [

        {
            'date': [
                {'name': 'div', 'attrs': {'class': 'ContentMetaDefault_date__wS0te'}},
            ],
            'text': [
                {'name': 'div', 'attrs': {'class': 'PageContentCommonStyling_text__CKOzO commonArticle_text__ul5uZ commonArticle_zoom__SDMjc'}},
            ]
        },

        {
            'date': [
                {'name': 'div', 'attrs': {'class': 'PageArticleHead_date__NRMcA'}},
            ],
            'text': [
                {'name': 'div', 'attrs': {'class': 'PageArticleContentStyling_text__scE9w commonArticle_text__ul5uZ'}},
            ]
        },

        {
            'date': [
                {'name': 'div', 'attrs': {'class': 'PageArticle_publishDate__v2Etv'}},  # 2 spans
            ],
            'text': [
                {'name': 'div', 'attrs': {'class': 'PageArticleContentStyling_text__iD61m commonArticle_text__ul5uZ'}},
            ]
        },

    ]


    for pattern in patterns:
        date = None
        text = None

        for date_selector in pattern['date']:
            date = find_elements_by_selectors(soup, [date_selector])
            if date:
                # 2 spans
                if (isinstance(date_selector, dict) and
                        date_selector.get('attrs', {}).get('class') == 'PageArticle_publishDate__v2Etv'):
                    date_cont = soup.find('div', attrs={'class': 'PageArticle_publishDate__v2Etv'})
                    if date_cont:
                        spans = date_cont.find_all('span')
                        if len(spans) == 2:
                            date_part = spans[0].get_text(strip=True)
                            time_part = spans[1].get_text(strip=True)
                            date = f"{date_part} {time_part}"
                if date:
                    break

        for text_selector in pattern['text']:
            text = find_elements_by_selectors(soup, [text_selector])
            if text:
                share_pos = text.rfind('Поделиться')
                if share_pos != -1:
                    text = text[:share_pos]
                text = text.strip()
                text = text.replace('/', '')
                text = text.replace('\\', '')
                break

        if date and text:
            logging.info(f"Found matching pattern: date={bool(date)}, text={bool(text)}")
            return {'date': date, 'text': text}

    return {'date': None, 'text': None}




def find_elements_by_selectors(soup, selectors, attr=None):
    for sel in selectors:
        try:
            if isinstance(sel, str):
                element = soup.select_one(sel)
            elif isinstance(sel, dict):
                element = soup.find(**sel)
            else:
                continue

            if element:
                if attr:
                    return element.get(attr)
                else:
                    return element.text.strip()


        except Exception as e:
            logging.error(f'Error parse elements by selectors: {e}')
            continue
    return None


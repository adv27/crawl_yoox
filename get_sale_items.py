__AUTHOR__ = 'anhvd'

import re
from multiprocessing.dummy import Pool as ThreadPool
from re import sub

import requests
from bs4 import BeautifulSoup

REQUIRED_SALE_PERCENT = float(40)
ORIGINAL_URL = 'https://www.yoox.com'
URL = r'https://www.yoox.com/hk/women/shoponline/leather%20jackets_c?dept=women&gender=D&page=2&attributes=%7b%27ctgr%27%3a%5b%27gbbttpll%27%5d%7d&season=X'


def save_to_html(items: []):
    for _list in items:
        for item in _list:
            append_html_file(item)


def append_html_file(item):
    anchor = item.find('a')
    anchor['href'] = ORIGINAL_URL + anchor['href']
    img = anchor.find('img')
    img['src'] = img['data-original']
    with open('result' + '.html', 'a', encoding='utf-8') as file:
        file.write(str(item))


def get_html_code(url: str):
    return requests.get(url=url).text


def get_items(url: str = None):
    if url is not None:
        html_code = get_html_code(url=url)
        soup = BeautifulSoup(html_code, 'html.parser')
        items = soup.find_all('div', {'id': re.compile('^item_')})
        return items
    return None


def items_filter(items: list, required_sale_percent: float):
    approved_items = []
    for item in items:
        old_price = item.find('span', {'class': 'oldprice text-linethrough text-light'})
        if old_price is not None:
            old_price = old_price.text
            old_price = float(sub(r'[^\d,]', '', old_price).replace(',', '.'))
            new_price = item.find('span', {'class': 'newprice font-bold'}).text
            new_price = float(sub(r'[^\d,]', '', new_price).replace(',', '.'))
            sale_percent = (new_price / old_price) * 100;
            if sale_percent <= required_sale_percent:
                # append_html_file(item=item)
                approved_items.append(item)
                brand = item.find('div', {'class': 'brand font-bold'}).text.strip()
                category = item.find('div', {'class': 'microcategory font-sans'}).text.strip()
                print('{} {} Old: {} New: {} After Sale Percent: {}'.
                      format(brand, category, old_price, new_price, sale_percent))
    return approved_items


def get_total_pages(url: str = None) -> int:
    '''
    :param url: the url of list items
    :return: number of pages
    '''
    if url is not None:
        html_code = get_html_code(url=url)
        soup = BeautifulSoup(html_code, 'html.parser')
        ul = soup.find('ul', {'class': 'pagination list-inline pull-right text-center js-pagination'})
        lis = ul.find_all('li')
        return int(lis[-2].text) \
            if ul.find('li', {'class': 'next-page'}) is not None \
            else int(lis[-1].text)
    return 0


def process(url):
    print(url)
    items = get_items(url)
    if items is not None:
        return items_filter(items=items, required_sale_percent=REQUIRED_SALE_PERCENT)
    return None


def main() -> int:
    total_pages = get_total_pages(url=URL)
    print("Total Pages: ", total_pages)
    if total_pages is not 0:
        urls = [re.sub('page=\d+', 'page=' + str(i), URL) for i in range(1, total_pages + 1)]
        pool = ThreadPool(20)
        result = pool.map(process, urls)
        pool.close()
        pool.join()
        save_to_html(result)
    return 0


if __name__ == '__main__':
    main()

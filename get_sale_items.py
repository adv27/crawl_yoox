__AUTHOR__ = 'anhvd'

import re
from re import sub
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import io

REQUIRED_SALE_PERCENT = float(25)
ORIGINAL_URL = 'https://www.yoox.com'
URL = r'https://www.yoox.com/hk/women/shoponline?dept=wprm_1712we&gender=D&page=1&size=3,4&season=X'
PATH_TO_CHROMEDRIVER = r'/home/anhvd/Downloads/chromedriver'

#driver = webdriver.Chrome(PATH_TO_CHROMEDRIVER)


def save_html(html_code, file_name):
    with io.open(file_name,'w',encoding='utf-8') as file:
        file.write(str(html_code))

def append_html_file(item):
    # make the img appear and change the link
    # print('Len: ', len(list_items))
    # for item in list_items:
    # print('Item: ', str(item))
    anchor = item.find('a')
    # print(str(anchor))
    anchor['href'] = ORIGINAL_URL + anchor['href']
    img = anchor.find('img')
    img['src'] = img['data-original']
    with open('result' + '.html', 'a', encoding='utf-8') as file:
        # for item in list_items:
        file.write(str(item))


def get_html_code(url: str):
    return requests.get(url=url).text


def get_items(url: str = None, index: int = None ):
    if url is not None:
        # driver.get(url=url)
        # html_code = driver.page_source
        html_code = get_html_code(url=url)
        # save_html(html_code,str(index) + '.html')
        soup = BeautifulSoup(html_code, 'html.parser')
        items = soup.find_all('div', {'id': re.compile('^item_')})
        return items
    return None


def items_filter(items: list, required_sale_percent: float):
    # approved_items = list()
    for item in items:
        old_price = item.find('span', {'class': 'oldprice text-linethrough text-light'})
        if old_price is not None:
            old_price = old_price.text
            old_price = float(sub(r'[^\d,]', '', old_price).replace(',', '.'))
            # old_price = [float(s.replace(',', '.')) for s in old_price.split() if s.replace(',', '').replace('.','').isdigit()][0]
            new_price = item.find('span', {'class': 'newprice font-bold'}).text
            new_price = float(sub(r'[^\d,]', '', new_price).replace(',', '.'))
            # new_price = [float(s.replace(',', '.')) for s in new_price.split() if s.replace(',', '').replace('.','').isdigit()][0]
            sale_percent = (new_price / old_price) * 100;
            if sale_percent <= required_sale_percent:
                # approved_items += item
                append_html_file(item=item)
                print('Old: ', old_price, ' New: ', new_price, ' Sale Percent', sale_percent)
                # print(len(approved_items))
                # return approved_items


def get_total_pages(url: str = None) -> int:
    '''

    :param url: the url of list items
    :return: number of pages
    '''
    if url is not None:
        html_code = get_html_code(url=url)
        soup = BeautifulSoup(html_code, 'html.parser')
        ul = soup.find('ul', {'class': 'pagination list-inline pull-right text-center js-pagination'})
        if ul.find('li', {'class': 'next-page'}) is not None:
            return int(ul.find_all('li')[-2].text)
        else:
            return int(ul.find_all('li')[-1].text)
    return 0


def main():
    total_pages = get_total_pages(url=URL)
    print("Total Pages: ", total_pages)
    if total_pages is not 0:
        # get all items from all pages
        for i in range(1, total_pages+1):
            url = re.sub('page=\d+', 'page=' + str(i), URL)
            # url = url.replace('#/','?')
            print(url)
            items = get_items(url=url,index=i)
            approved_items_len = 0
            if items is not None:
                # approved_items = items_filter(items=items, required_sale_percent=REQUIRED_SALE_PERCENT)
                items_filter(items=items, required_sale_percent=REQUIRED_SALE_PERCENT)
                # approved_items_len = len(approved_items)
                # print('Approved items len: ', approved_items_len)
                # append_html_file(list_items=approved_items)
            print('Page: ', i, ' Items: ', len(items))

    return 0


if __name__ == '__main__':
    main()
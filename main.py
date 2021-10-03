import logging

import bs4
import requests


class LabirintParser:

    def __init__(self, url):
        self._url = url
        self._result = []
        self._session = requests.Session()
        self._session.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Accept-Language': 'ru',
        }
        self._domain = 'https://www.labirint.ru'

    def load_page(self, url: str):
        response = self._session.get(url)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return bs4.BeautifulSoup(response.text, 'lxml')

    def parse_page(self, soup: bs4.BeautifulSoup):
        cards = soup.select('div.card-column')
        for card in cards:
            self.parse_card(card)

    def parse_card(self, card: bs4.Tag):
        url_block = card.select_one('a.cover')
        if not url_block:
            logging.error('URL not found')
            return
        url = self._domain + url_block.get('href')

        image = card.select_one('img.book-img-cover')
        if not image:
            logging.error('Image not found')
            return
        img_url = image.get('data-src')

        new_price_block = card.select_one('span.price-val')
        if new_price_block:
            price = new_price_block.select_one('span').text
        else:
            price = card.select_one('span.price-old').select_one('span').text

        soup = self.load_page(url)
        detail = soup.select_one('div.product-description')
        authors_list = detail.select('div.authors')

        if not authors_list:
            logging.error('Author not found')
            return
        authors = [author.text for author in authors_list]

        publisher_block = detail.select_one('div.publisher')
        if not publisher_block:
            logging.error('Publisher not found')
            return
        publisher = publisher_block.text

        articul_block = detail.select_one('div.articul')
        if not articul_block:
            logging.error('Articul not found')
            return
        articul = articul_block.text

        pages_block = detail.select_one('div.pages2')
        if not pages_block:
            logging.error('Pages not found')
            return
        pages = pages_block.text

        book = {
            'url': url,
            'img_url': img_url,
            'price': price,
            'author': authors,
            'publisher': publisher,
            'id': articul,
            'pages': pages,
        }
        self._result.append(book)

    def run(self):
        soup = self.load_page(self._url)
        self.parse_page(soup)


if __name__ == '__main__':
    labirint = LabirintParser('https://www.labirint.ru/search/python/?stype=0')
    labirint.run()
    print(labirint._result)

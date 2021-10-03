import asyncio
import datetime
import logging

import aiohttp
import bs4


result = []
url = 'https://www.labirint.ru/search/python/?stype=0'


class LabirintParser:

    def __init__(self, url: str):
        self._url = url
        self._domain = 'https://www.labirint.ru'

    async def load_page(self, url: str):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Accept-Language': 'ru',
        }
        async with aiohttp.ClientSession() as session:
            response = await session.get(url=url, headers=headers)
            response_text = await response.text()
        return bs4.BeautifulSoup(response_text, 'lxml')

    async def parse_page(self, soup: bs4.BeautifulSoup):
        cards = soup.select('div.card-column')
        for card in cards:
            await self.parse_card(card)

    async def parse_card(self, card: bs4.Tag):
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

        soup = await self.load_page(url)
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
        result.append(book)

    async def run(self):
        soup = await self.load_page(self._url)
        await self.parse_page(soup)


async def gather_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Accept-Language': 'ru',
    }
    async with aiohttp.ClientSession() as session:
        response = await session.get(url=url, headers=headers)
        response_text = await response.text()
        soup = bs4.BeautifulSoup(response_text, 'lxml')

        count_page = int(soup.select('a.pagination-number__text')[-1].text)

        tasks = []

        for page in range(1, count_page + 1):
            labirint = LabirintParser(url + f'&page={page}')
            task = asyncio.create_task(labirint.run())
            tasks.append(task)

        await asyncio.gather(*tasks)


def main():
    start_time = datetime.datetime.utcnow()
    asyncio.run(gather_data())
    print(result)
    end_time = datetime.datetime.utcnow()
    print(end_time - start_time)


if __name__ == '__main__':
    main()

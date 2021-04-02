import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from flagstar.items import Article


class flagstarSpider(scrapy.Spider):
    name = 'flagstar'
    start_urls = ['http://investors.flagstar.com/IRW/News/109084']
    page = 1

    def parse(self, response):
        links = response.xpath('//h4/a/@href').getall()
        if links:
            yield from response.follow_all(links, self.parse_article)

            self.page += 1

            next_page = f'http://investors.flagstar.com/News/109084/NewsData?pageIndex={self.page}'
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="irwFilePageDate"]/text()').get()
        if date:
            date = date.split()[-1]

        content = response.xpath('//div[@class="xn-content"]//text()').getall()
        content = [text for text in content if text.strip() and '{' not in text]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()

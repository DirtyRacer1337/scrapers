import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class PutaLocuraSpider(BaseSceneScraper):
    name = 'PutaLocura'
    network = 'Puta Locura'
    parent = 'Puta Locura'
    site = 'Puta Locura'

    start_urls = [
        'https://www.putalocura.com',
    ]

    selector_map = {
        'title': '//h1/span[@class="model-name"]/text()',
        'description': '//div[contains(@class,"description")]/p//text()',
        'date': '//div[@class="released-views"]/span[1]/text()',
        'date_formats': ['%d/%m/%Y'],
        'image': '//script[contains(text(), "fluidPlayer")]/text()',
        're_image': r'posterImage: ?\"(.*?)\"',
        'performers': '',  # They can be pulled with '//span[@class="site-name"]/text()', but halfway through the same spot becomes sites or categories instead
        'tags': '',
        'external_id': r'.*\/(.*?)$',
        'trailer': '',
        'pagination': '/en?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="widget-release-card"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_performers(self, response):
        return []

    def get_tags(self, response):
        return ["Spanish"]

    def get_title(self, response):
        title = response.xpath('//title/text()')
        if title:
            title = title.get()
            if "|" in title:
                title = re.search(r'(.*?)\|', title).group(1)
        if not title:
            title = self.process_xpath(response, self.get_selector_map('title')).get()
            if "|" in title:
                title = re.search(r'(.*)\|', title).group(1)

        title = title.strip()
        if title[0] == "!" or title[0] == "?" or title[0] == "¡" or title[0] == "¿":
            title = title[1:]

        if title:
            return self.cleanup_title(title)
        else:
            return ''

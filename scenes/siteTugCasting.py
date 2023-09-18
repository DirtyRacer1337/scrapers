import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTugCastingSpider(BaseSceneScraper):
    name = 'TugCasting'
    network = 'Tug Casting'

    start_urls = [
        'https://tugcasting.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@class="video-text"]/div[contains(@style,"white")]/text()',
        'date': '//p[contains(text(),"Added")]/text()',
        're_date': 'on: (.*)',
        'date_formats': ['%b %d, %Y'],
        'image': '//video/@poster',
        'performers': '//div[@class="model-tags"]/a[contains(@href, "/model/")]/text()',
        'tags': '//div[@class="model-tags"]/a[contains(@href, "/search/")]/text()',
        'duration': '//p[contains(text(), "Length:")]/text()',
        're_duration': r'(\d{1,2}\:\d{2})',
        'external_id': r'.*/(.*?)/$',
        'trailer': '',
        'pagination': '/page%s'
    }

    cookies = {'SPSI': '0ca00a563fecd2d832cda91ab94f1fe9'}

    def get_scenes(self, response):
        scenes = response.xpath('//h3/a/@href|//div[@class="video-thumb"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, cookies=self.cookies, headers=self.headers)

    def get_site(self, response):
        return "Tug Casting"

    def get_parent(self, response):
        return "Tug Casting"

    def get_description(self, response):
        description = self.process_xpath(response, self.get_selector_map('description')).getall()
        if description:
            description = " ".join(description)
            return self.cleanup_description(description)
        return ''

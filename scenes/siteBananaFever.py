import re
import html
import json
import requests
import unidecode
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteBananaFeverSpider(BaseSceneScraper):
    name = 'BananaFever'

    custom_settings = {'CONCURRENT_REQUESTS': '1',
                       'AUTOTHROTTLE_ENABLED': 'True',
                       'AUTOTHROTTLE_DEBUG': 'False',
                       'DOWNLOAD_DELAY': '2',
                       'CONCURRENT_REQUESTS_PER_DOMAIN': '1',
                       }

    start_urls = [
        'https://bananafever.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/index.php/wp-json/wp/v2/posts?page=%s&per_page=20'
    }

    def start_requests(self):
        tagdata = []
        for i in range(1, 10):
            req = requests.get(f'https://bananafever.com/index.php/wp-json/wp/v2/categories?per_page=100&page={str(i)}')
            if req and len(req.text) > 5:
                tagtemp = []
                tagtemp = json.loads(req.text)
                tagdata = tagdata + tagtemp
            else:
                break

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page),
                                 callback=self.parse,
                                 meta={'page': self.page, 'tagdata': tagdata},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        jsondata = json.loads(response.text)
        for scene in jsondata:
            item = SceneItem()
            # ~ if 'og_image' in scene["yoast_head_json"]:
            # ~ item['image'] = scene["yoast_head_json"]['og_image'][0]['url']
            # ~ item['image_blob'] = self.get_image_blob_from_link(item['image'])
            # ~ else:
            # ~ item['image'] = ""
            # ~ item['image_blob'] = ""

            item['id'] = str(scene['id'])
            item['date'] = scene['date']
            item['title'] = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', scene['title']['rendered'])).strip())
            item['tags'] = ['Asian', 'Interracial']
            item['trailer'] = None
            item['description'] = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', scene['excerpt']['rendered'])).strip())
            if 'vc_raw_html' in item['description']:
                item['description'] = ''
            item['performers'] = []
            for category in scene['categories']:
                if '105' not in str(category) and '106' not in str(category) and '170' not in str(category) and '163' not in str(category):
                    for tag in meta['tagdata']:
                        if tag['id'] == category:
                            item['tags'].append(tag['name'])
            if "Upcoming" in item['tags']:
                item['tags'].remove("Upcoming")
            item['site'] = 'Banana Fever'
            item['parent'] = 'Banana Fever'
            item['network'] = 'Banana Fever'
            item['url'] = scene['link']

            meta['item'] = item

            if "wp:attachment" in scene['_links'] and scene['_links']['wp:featuredmedia'][0]['href']:
                image_url = scene['_links']['wp:featuredmedia'][0]['href']
            else:
                image_url = None

            item['image'] = None
            item['image_blob'] = None
            if image_url:
                req = requests.get(image_url)
                if req and len(req.text) > 5:
                    imagerow = json.loads(req.text)
                else:
                    imagerow = None

                if imagerow and 'guid' in imagerow:
                    if 'rendered' in imagerow['guid'] and imagerow['guid']['rendered']:
                        item['image'] = imagerow['guid']['rendered']
                        item['image_blob'] = self.get_image_blob_from_link(item['image'])

            if " - Demo" not in item['title'] and " - Trailer" not in item['title']:
                yield item

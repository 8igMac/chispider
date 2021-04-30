import scrapy
from scrapy.crawler import CrawlerProcess
import logging
import time

# class MyLogFormatter(scrapy.logformatter.LogFormatter):
#     def scraped(self, item, response, spider):
#         """Logs a message when an item is scraped by a spider."""
#         if isinstance(response, Failure):
#             src = response.getErrorMessage()
#         else:
#             #src = response
#             src = 'yoyo'
#         return {
#             'level': logging.DEBUG,
#             'msg': SCRAPEDMSG,
#             'args': {
#                 'src': src,
#                 'item': item,
#             }
#         }

class NewsSpider(scrapy.Spider):
    name = "news"

    custom_settings = {
        'FEED_EXPORT_ENCODING': 'utf-8',
#        'LOG_LEVEL': logging.INFO,
#        'LOG_FORMATTER': MyLogFormatter,
    }

    start_urls = [
        'https://www.cna.com.tw/'
    ]

    # Click on the category list above the main page.
    def parse(self, response):
        print(f"Existing settings: {self.settings.attributes.keys()}") # debug
        categroy_links = response.xpath('//*[@id="pnProductNavContents"]/ul/li/a/@href').getall()
        yield from response.follow_all(categroy_links, self.parse_hot_keyword)

    # Click on the hot keyword section.
    def parse_hot_keyword(self, response):
        hot_keyword_links = response.xpath('//*[@id="scrollable"]/div/div/div/div[3]/div[2]/div[2]/div[2]/a/@href').getall()
        yield from response.follow_all(hot_keyword_links, self.parse_article_index)

    # Click each article
    def parse_article_index(self, response):
        article_links = response.xpath('//*[@id="jsMainList"]/li/a/@href').getall()
        yield from response.follow_all(article_links, self.parse_article)

    def parse_article(self, response):
        title = response.xpath('//div[has-class("centralContent")]/h1/span/text()').get()

        release_time = response.xpath('//div[has-class("updatetime")]/span/text()').get()

        category = response.xpath('//div[has-class("breadcrumb")]/a[has-class("blue")]/text()').get()

        paragraphs = response.xpath('//div[has-class("paragraph")]/p/text()').getall() 
        reporter = paragraphs[0][1:9] # FIXME: Assume reporter's name has 3 words.

        content = ''
        for paragraph in paragraphs:
            content += paragraph
        # FIXME: Very rough parsing.
        content_begin = content.find('）') + 2
        content_end = content.find('編輯') - 1
        content = content[content_begin : content_end] 

        yield {
            'title': title,
            'release-time': release_time,
            'reporter': reporter,
            'category': category,
            'content': content,
        }

if __name__ == "__main__":
    process = CrawlerProcess(settings={
        "FEEDS": {
            "cna_news.json": {"format": "json"},
        },
    })

    process.crawl(NewsSpider)
    start = time.time()
    process.start()
    print("Time elapse: ", time.time() - start)


# -*- coding: utf-8 -*-
import os
import glob
from scrapy import Spider
#from time import sleep
#from selenium import webdriver
#from scrapy.selector import Selector
from scrapy.http import Request
#from selenium.common.exceptions import NoSuchElementException
from scrapy.loader import ItemLoader
from books_crawler.items import BooksCrawlerItem

def product_info(response, value):
    return response.xpath('//th[text()="' + value + '"]/following-sibling::td/text()').extract_first()

class BooksSpider(Spider):
    name = 'books'
    allowed_domains = ['books.toscrape.com']
    start_urls = ['http://books.toscrape.com']

    # arguments
    # def __init__(self, category):
    #     self.start_urls = [category]


    # def start_requests(self):
    #     self.driver = webdriver.Chrome('C:\webdrivers\chromedriver.exe')
    #     self.driver.get('http://books.toscrape.com/')

    #     sel = Selector(text=self.driver.page_source)
    #     books = sel.xpath('//h3/a/@href').extract()
    #     for book in books:
    #         url = 'http://books.toscrape.com/' + book
    #         yield Request(url, callback=self.parse_book)

    #     while True:
    #         try:
    #             next_page = self.driver.find_element_by_xpath('//a[text()="next"]')
    #             sleep(3)
    #             self.logger.info('Sleeping for 3 seconds.')
    #             next_page.click()

    #             sel = Selector(text=self.driver.page_source)
    #             books = sel.xpath('//h3/a/@href').extract()
    #             for book in books:
    #                 url = 'http://books.toscrape.com/' + book
    #                 yield Request(url, callback=self.parse_book)

    #         except NoSuchElementException as e:
    #             self.logger.info('No more pages to load.')
    #             self.driver.quit()
    #             break

    def parse(self, response):
        books = response.xpath('//h3/a/@href').extract()
        for book in books:
            absolute_url = response.urljoin(book)
            yield Request(absolute_url, callback=self.parse_book)
        # process next page
        next_page_url = response.xpath('//a[text()="next"]/@href').extract_first()
        absolute_next_page_url = response.urljoin(next_page_url)
        yield Request(absolute_next_page_url)

    def parse_book(self, response):
        l = ItemLoader(item=BooksCrawlerItem(), response=response)
        title = response.css('h1::text').extract_first()
        price = response.xpath('//*[@class="price_color"]/text()').extract_first()

        image_urls = response.xpath('//img/@src').extract_first()
        image_urls = image_urls.replace('../..', 'http://books.toscrape.com/')

        l.add_value('image_urls', image_urls)

        yield l.load_item()

        rating = response.xpath('//*[contains(@class, "star-rating")]/@class').extract_first()
        rating = rating.replace('star-rating', '')

        description = response.xpath('//*[@id="product_description"]/following-sibling::p/text()').extract_first()

        # product informatoion data points
        upc =  product_info(response, 'UPC')
        product_type = product_info(response, 'Product Type')
        price_including_tax = product_info(response, 'Price (excl. tax)')
        price_excluding_tax = product_info(response, 'Price (incl. tax)')
        tax = product_info(response, 'Tax')
        availability = product_info(response, 'Availability')
        number_of_reviews = product_info(response, 'Number of reviews')

        yield {
            'title': title,
            'price': price,
            # 'image_urls': image_urls,
            'rating': rating,
            'description': description,
            'upc' : upc,
            'product_type' : product_type,
            'price_including_tax' : price_including_tax,
            'price_excluding_tax' : price_excluding_tax,
            'tax' : tax,
            'availability' : availability,
            'number_of_reviews' : number_of_reviews
        }

    # def close(self, reason):
    #     csv_file = max(glob.iglob('*.csv'), key=os.path.getctime)
    #     os.rename(csv_file, 'footbar.csv')
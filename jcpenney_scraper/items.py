# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JcpenneyScraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()
    product_name = scrapy.Field()
    current_price = scrapy.Field()
    original_price = scrapy.Field()
    discount = scrapy.Field()
    features = scrapy.Field()
    description = scrapy.Field()
    image_urls = scrapy.Field()
    rating = scrapy.Field()
    review_count = scrapy.Field()
    sizes = scrapy.Field()
    colors = scrapy.Field()
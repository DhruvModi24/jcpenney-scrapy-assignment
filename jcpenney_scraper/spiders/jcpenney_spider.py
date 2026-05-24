import scrapy
import json
from jcpenney_scraper.items import JcpenneyScraperItem
import re
from scrapy import Selector
from scrapy.cmdline import execute

class JcpenneySpiderSpider(scrapy.Spider):
    name = "jcpenney_spider"
    allowed_domains = ['jcpenney.com', 'search-api.jcpenney.com']
    custom_headers = {
        'referer': 'https://www.jcpenney.com/',
    }
    search_term = 'tshirt'
    api_url = f'https://search-api.jcpenney.com/v1/search-service/s?productGridView=medium&searchTerm={search_term}&responseType=organic'

    visited_urls = set()

    def start_requests(self):
        try:
            yield scrapy.Request(
                url=self.api_url,
                headers=self.custom_headers,
                callback=self.parse,
                errback=self.handle_error,
                dont_filter=True
            )
        except Exception as e:
            self.logger.error(f"Error in start_requests: {e}")

    def parse(self, response):
        try:
            data = json.loads(response.text)

            totalNum_records = data.get('organicZoneInfo', {}).get('totalNumRecs', [])
            self.logger.info(
                f'Found totalNumRecs: {totalNum_records} from Search: {self.search_term}'
            )

            # Calculate total pages based on 48 products per page
            total_pages = (totalNum_records // 48) + 1 if totalNum_records > 0 else 1
            self.logger.info(
                f'Calculated total pages: {total_pages} for Search: {self.search_term}'
            )

            for page in range(1, total_pages + 1):
                # scrape until page 2 for testing, remove the condition to scrape all pages
                if page > 2:
                    break
                api_url = f'https://search-api.jcpenney.com/v1/search-service/s?productGridView=medium&searchTerm={self.search_term}&page={page}&responseType=organic'
                yield scrapy.Request(
                    url=api_url,
                    headers=self.custom_headers,
                    callback=self.parse_search_api,
                    errback=self.handle_error,
                    dont_filter=True
                )
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error in parse: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error in parse: {e}")

    def parse_search_api(self, response):
        try:
            """Parse product listing JSON API"""

            data = json.loads(response.text)

            products = data.get('organicZoneInfo', {}).get('products', [])

            self.logger.info(
                f'Found {len(products)} products from API: {response.url}'
            )

            for product in products:
                try:
                    product_url = product.get('pdpUrl','')
                    product_name = product.get('name','').strip()

                    if not product_url:
                        self.logger.warning("Product URL missing, skipping")
                        continue

                    product_rating = product.get('averageRating', '')
                    product_review_count = product.get('reviewCount', '')

                    product_price = product.get('currentMin', '')
                    original_price = product.get('originalMin', '')
                    discount = product.get('maxSavePrice', '')

                    if discount == float(0.00) or discount == '':
                        # calculate discount if not provided
                        try:
                            if product_price and original_price and float(original_price) > 0:
                                discount = f"{round((float(original_price) - float(product_price)) / float(original_price) * 100)}"
                            else:
                                discount = ''
                        except Exception as e:
                            self.logger.warning(f"Error calculating discount: {e}")
                            discount = ''

                    full_url = f'https://www.jcpenney.com{product_url}'

                    if full_url in self.visited_urls:
                        self.logger.debug(f"URL already visited: {full_url}")
                        continue

                    self.visited_urls.add(full_url)

                    self.logger.info(f'Scheduling product: {product_name} | URL: {full_url}')

                    yield scrapy.Request(
                        url=full_url,
                        headers=self.custom_headers,
                        callback=self.parse_product,
                        errback=self.handle_error,
                        meta={
                            'product_name': product_name,
                            'product_url': full_url,
                            'product_rating': product_rating,
                            'product_review_count': product_review_count,
                            'product_price': product_price,
                            'original_price': original_price,
                            'discount': discount
                        }
                    )
                except Exception as e:
                    self.logger.error(f"Error processing product: {e}")
                    continue
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error in parse_search_api: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error in parse_search_api: {e}")

    def parse_product(self, response):
        try:
            item = JcpenneyScraperItem()

            # Extract basic metadata
            item['url'] = response.meta.get('product_url','')
            item['product_name'] = response.meta.get('product_name')
            item['current_price'] = response.meta.get('product_price', '')
            item['original_price'] = response.meta.get('original_price', '')
            item['discount'] = response.meta.get('discount', '')
            item['rating'] = response.meta.get('product_rating', '')
            item['review_count'] = response.meta.get('product_review_count', '')

            # Extract colors and sizes
            try:
                Product_variation_json_text = response.css('script[type="application/ld+json"]::text').get('')

                Product_variation_json = json.loads(Product_variation_json_text) if Product_variation_json_text else {}

                color = []
                size = []
                color_size_info = Product_variation_json.get('hasVariant', [])
                for variant in color_size_info:
                    if 'color' in variant:
                        color.append(variant['color'])
                    if 'size' in variant:
                        size.append(variant['size'])

                item['colors'] = ' , '.join(list(set(color))) if color else ''
                item['sizes'] = ' , '.join(list(set(size))) if size else ''
            except Exception as e:
                self.logger.warning(f"Error extracting colors/sizes: {e}")
                item['colors'] = ''
                item['sizes'] = ''

            # Extract product details
            try:
                html = response.text
                description = ''
                features = ''
                image_urls = ''

                if "__PRELOADED_STATE__" in html:

                    match = re.search(r'window\.__PRELOADED_STATE__\s*=\s*({.*?});', html, re.DOTALL)

                    if match:
                        data_str = match.group(1)

                        js_object  = re.sub(r':undefined', ':null', data_str)
                        js_object = re.sub(r',\s*}', '}', js_object)
                        Product_detail_json_text = re.sub(r',\s*]', ']', js_object)
                        try:
                            Product_detail_json = json.loads(Product_detail_json_text)

                            # Safely extract description
                            try:
                                description_text = Product_detail_json.get('productDetails', {}).get('lots', [{}])[0].get(
                                    'description', '')
                                if description_text:
                                    description_obj = Selector(text=description_text)
                                    description = description_obj.xpath("//p//text()").get("").strip()
                                    bullets_points = [bullet.get().strip() for bullet in
                                                      description_obj.xpath("//ul/li/text()")]
                                    features = " | ".join(bullets_points) if bullets_points else ''
                            except (IndexError, AttributeError, TypeError) as e:
                                self.logger.warning(f"Error extracting description: {e}")

                            # Safely extract images
                            try:
                                image_data = Product_detail_json.get('productDetails', {}).get('images', [])
                                image_urls_list = [img['url'] for img in image_data if isinstance(img, dict) and 'url' in img]
                                image_urls = ' | '.join(list(set(image_urls_list))) if image_urls_list else ''
                            except Exception as e:
                                self.logger.warning(f"Error extracting images: {e}")

                        except json.JSONDecodeError as e:
                            self.logger.warning(f"JSON decode error in product details: {e}")
                    else:
                        self.logger.warning("PRELOADED_STATE not found in HTML")

                item['description'] = description
                item['features'] = features
                item['image_urls'] = image_urls

            except Exception as e:
                self.logger.error(f"Error extracting product details: {e}")
                item['description'] = ''
                item['features'] = ''
                item['image_urls'] = ''

            yield item
        except Exception as e:
            self.logger.error(f"Critical error in parse_product: {e}")

    def handle_error(self, failure):
            self.logger.error(f"Request failed: {failure.request.url} | Error: {failure.value}")

if __name__ == "__main__":
    execute("scrapy crawl jcpenney_spider".split())
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from itemadapter import ItemAdapter
import json
import csv
import logging


class JcpenneyScraperPipeline:
    """Pipeline to save scraped items to both JSON and CSV formats."""

    def open_spider(self, spider):
        # JSON file setup
        self.json_file = open(
            "jcpenney_products.json",
            "w",
            encoding="utf-8"
        )
        self.json_file.write("[\n")
        self.first_item = True

        # CSV file setup
        self.csv_file = open(
            "jcpenney_products.csv",
            "w",
            newline="",
            encoding="utf-8"
        )
        self.csv_writer = None
        self.csv_headers_written = False

    def close_spider(self, spider):
        """Close file handles when spider finishes."""
        try:
            self.json_file.write("\n]")
            self.json_file.close()
            self.csv_file.close()
            spider.logger.info("Files closed successfully")
        except Exception as e:
            spider.error(f"Error closing files: {e}")

    def process_item(self, item, spider):
        """Process each item and write to both JSON and CSV."""
        try:
            item_dict = dict(ItemAdapter(item))

            if item.__class__.__name__ == "JcpenneyScraperItem":

                # Write to JSON
                self._write_to_json(item_dict)

                # Write to CSV
                self._write_to_csv(item_dict)

                return item

        except Exception as e:
            spider.error(f"Error processing item: {e}")
            raise

    def _write_to_json(self, item_dict):
        """Write item to JSON file with proper formatting."""
        if not self.first_item:
            self.json_file.write(",\n")

        line = json.dumps(
            item_dict,
            ensure_ascii=False,
            indent=4
        )
        self.json_file.write(line)
        self.first_item = False

    def _write_to_csv(self, item_dict):
        """Write item to CSV file with header row on first item."""
        if not self.csv_headers_written:
            self.csv_writer = csv.DictWriter(
                self.csv_file,
                fieldnames=item_dict.keys()
            )
            self.csv_writer.writeheader()
            self.csv_headers_written = True

        self.csv_writer.writerow(item_dict)
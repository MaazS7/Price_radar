# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
import pymongo
# from scrapy.exceptions import DropItem
import datetime
from pymongo.errors import DuplicateKeyError



class MongoDBPipeline:
    def __init__(self, mongo_uri, mongo_db, collection_name):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.collection_name = collection_name

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE'),
            collection_name=crawler.settings.get('MONGO_COLLECTION', 'testing'),
        )
    
    
    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri,serverSelectionTimeoutMS=30000,connectTimeoutMS=30000,socketTimeoutMS=30000)
        self.db = self.client[self.mongo_db]
        self.db[self.collection_name].create_index("url", unique=True)

    def close_spider(self, spider):
        self.client.close()


    def process_item(self, item, spider):

        if spider.name == 'daraz_query' or spider.name == 'priceoye_query' or spider.name == 'shophive_query':

            collection = self.db["products"]
            # existing_product = collection.find_one({"url": item["url"]})

            now = datetime.datetime.now(datetime.timezone.utc)

            item["original_price"] = item["price"]
            item["current_price"] = item["price"]
            item["previous_price"] = None
            item["last_updated"] = now
            collection.insert_one(dict(item))
            # twelve_hours_ago = now - datetime.timedelta(hours=12)

            # if existing_product:
            #     last_updated = existing_product.get("last_updated", None)

            #     if last_updated >= twelve_hours_ago:
            #         return existing_product
                
            #     # Check if there's a discount
            #     original_price = existing_product.get("original_price", item["price"])
            #     discount = original_price - item["price"]
            #     if discount > 0:
            #         print(f"🚀 Discount detected! {original_price} → {item['price']} (Saved: {discount})")

            #     # Update the product
            #     collection.update_one(
            #         {"url": item["url"]},
            #         {"$set": {
            #             "name": item["name"],
            #             "image_url": item["image_url"],
            #             "previous_price": existing_product["current_price"],
            #             "current_price": item["price"],
            #             "last_updated": now
            #         }}
            #     )
            # else:
                # Insert new product
                

            
            return item
        
        elif spider.name == 'daraz_category' or spider.name == 'shophive_category' or spider.name == 'priceoye_category':

            collection = self.db["products"]
            # existing_product = collection.find_one({"url": item["url"]})

            now = datetime.datetime.now(datetime.timezone.utc)

            item["original_price"] = item["price"]
            item["current_price"] = item["price"]
            item["previous_price"] = None
            item["last_updated"] = now
            try:
                collection.insert_one(dict(item))
            except DuplicateKeyError:
            # Skip if document already exists
                spider.logger.debug(f"Duplicate item found: {item['url']}")
            except Exception as e:
                spider.logger.error(f"Error inserting item: {e}")


            return item
        
        elif spider.name == 'daraz_single_product':

            if item["price"] == None:
                return
            
            else:
                collection = self.db["products"]
                now = datetime.datetime.now(datetime.timezone.utc)

                existing_item = collection.find_one({"url": item["url"]})
                if existing_item:
                    collection.update_one(
                        {"_id": existing_item["_id"]},
                        {
                            "$set": {
                                "previous_price": existing_item["current_price"],
                                "current_price": item["price"],
                                "last_updated": now
                            }
                        }
                    )

            return item



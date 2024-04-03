# -*- coding: utf-8 -*-
import json
import logging
import os


from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

from flickr.items import FlickrImage, FlickrPhotoset


class FlickrImagePipeline(object):
    
    output_dir = 'output'
    
    def open_spider(self, spider):
        self.file = open("photos.jsonl", "w")
        if not os.path.exists(FlickrImagePipeline.output_dir):
            os.makedirs(FlickrImagePipeline.output_dir)
    
    def process_item(self, item, spider):
        if isinstance(item, FlickrImage):
            filename = item['url'].split('/')[-1]
            with open(os.path.join(FlickrImagePipeline.output_dir, filename), 'wb') as f:
                f.write(item['content'])
            data = ItemAdapter(item)
            del data['content']
            line = json.dumps(data.asdict(), ensure_ascii=False) + '\n'
            self.file.write(line)
        return item
        
class FlickrPhotosetPipeline(object):
    def open_spider(self, spider):
        self.file = open("photosets.jsonl", "w")

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        if isinstance(item, FlickrPhotoset):
            line = json.dumps(ItemAdapter(item).asdict(), ensure_ascii=False) + "\n"
            self.file.write(line)
        return item
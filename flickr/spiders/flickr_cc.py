# -*- coding: utf-8 -*-
import logging
import os

import scrapy
from scrapy.utils.defer import maybe_deferred_to_future

from flickr.items import FlickrImage, FlickrPhotoset


class FlickrCcSpider(scrapy.Spider):
    name = 'flickr_cc'
    allowed_domains = ['flickr.com', 'staticflickr.com']
    start_urls = [
        f'https://www.flickr.com/services/rest/?method=flickr.photosets.getList&api_key={os.environ["FLICKR_KEY"]}&user_id={os.environ["FLICKR_UID"]}&format=rest'
    ]

    def parse(self, response):
        for photoset in response.css('photoset'):
            description = photoset.xpath('description/text()').get()
            yield scrapy.Request(photoset_url(photoset), self.handle_photoset, cb_kwargs={'description': description})
            
    async def handle_photoset(self, response, description):
        photoset = response.css('photoset')
        title = photoset.xpath('@title').get()
        photo_urls = [photo_url(photo) for photo in response.css('photo')]
        url = photoset_web_url(photoset)
        yield FlickrPhotoset(url=url, title=title, description=description, photos=photo_urls)
        for photo in response.css('photo'):
            # download photo info
            deferred = self.crawler.engine.download(scrapy.Request(photo_info_url(photo)))
            photo_info = await maybe_deferred_to_future(deferred)
            tags = [tag.get() for tag in photo_info.xpath('//tags/tag').xpath('@raw')]
            date_taken = photo_info.xpath('//dates/@taken').get()
            description = photo_info.xpath('//description/text()').get()
            photopage = photo_info.xpath('//url[@type="photopage"]/text()').get()
            # download image
            deferred = self.crawler.engine.download(scrapy.Request(photo_url(photo)))
            response = await maybe_deferred_to_future(deferred)
            yield FlickrImage(url=response.url, content=response.body, date=date_taken, tags=tags, description=description, photopage=photopage)


def photoset_web_url(photoset):
    return 'https://www.flickr.com/photos/{user_id}/albums/{photoset_id}'.format(
        user_id=photoset.xpath('@owner').get(),
        photoset_id=photoset.xpath('@id').get(),
    )

def photoset_url(photoset):
    return 'https://flickr.com/services/rest/?method=flickr.photosets.getPhotos&api_key={api_key}&user_id={user_id}&photoset_id={photoset_id}'.format(
        api_key=os.environ['FLICKR_KEY'],
        user_id=photoset.xpath('@owner').get(),
        photoset_id=photoset.xpath('@id').get()
    )


def photo_url(photo):
    return 'https://live.staticflickr.com/{server}/{id}_{secret}_{size}.jpg'.format(
        server=photo.xpath('@server').get(),
        id=photo.xpath('@id').get(),
        secret=photo.xpath('@secret').get(),
        size='b',  # TODO for size "o" (original), we need to call flickr.photos.getSizes to get the `size original` source
    )

def photo_info_url(photo):
    return 'https://www.flickr.com/services/rest/?method=flickr.photos.getInfo&api_key={api_key}&user_id={user_id}&photo_id={photo_id}&format=rest'.format(
        api_key=os.environ['FLICKR_KEY'],
        user_id=photo.xpath('@owner').get(),
        photo_id=photo.xpath('@id').get()
    )

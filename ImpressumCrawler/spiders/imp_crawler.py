# -*- coding: utf-8 -*-
import scrapy
import requests
from ImpressumCrawler.items import ImpressumcrawlerItem
import re
from bs4 import BeautifulSoup
from ..obtain_urls import ImpressumUrls, LogoUrls
from ..process_all import ProcessAll
from scrapy_splash import SplashRequest

script = """
function main(splash, args)
  splash.images_enabled = false
  assert(splash:go(args.url))
  assert(splash:wait(args.wait))
  js = string.format("document.querySelector('#mainsrp-pager div.form > input').value=%d;document.querySelector('#mainsrp-pager div.form > span.btn.J_Submit').click()", args.page)
  splash:evaljs(js)
  assert(splash:wait(args.wait))
  return splash:html()
end
"""
url_lists = ['www.dkb.de', 'www.msg.group','www.db.com','www.apple.com','www.rockit-internet.de',
            'www.hollinradoske.de','www.cenior.de', 'www.1und1.de','www.vodafone.de','www.vodafone.ro',
             'www.tripit.com','www.emmy-sharing.de', 'www.samsung.com', 'www.airbus.com', 'www.volkswagen.de',
             'www.bmw.de', 'www.bmwgroup.com','www.intelligence-airbusds.com','www.xbird.io']

final_impressums =ImpressumUrls(url_lists).obtain_impressum_urls()

class ImpressumCrawlerSpider(scrapy.Spider):
    name = 'imp_crawler'
    start_urls = final_impressums

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse,
                                endpoint='render.html',
                                args={'wait': 0.5},
                                )

    def parse(self, response):
        urls = response.url
        urls_split = urls.split('/')
        base_url = urls_split[0]+'//'+urls_split[2]
        response_data = response.xpath('//div//*/text()').extract()
        response_a = response.xpath("//a")
        response_div = response.xpath("//div")
        logos = LogoUrls(response_a, response_div).obtain_logo_src(base_url)
        comp_names = ProcessAll(response_data).process_comp_names()
        emails = ProcessAll(response_data).process_emails()
        fax = ProcessAll(response_data).process_fax()
        telephone = ProcessAll(response_data).process_telephone()
        address = ProcessAll(response_data).process_address()
        item = ImpressumcrawlerItem()
        item['urls'] = urls
        item['comp_names'] = comp_names
        item['emails'] = emails
        item['fax'] = fax
        item['telephone'] = telephone
        item['address'] = address
        item['image_urls'] = logos
        return item

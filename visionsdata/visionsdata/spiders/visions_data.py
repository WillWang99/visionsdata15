##########################################################################################
#USAGE: scrapy crawl visionsdata  
#Product information: title, url, availability, current_price, regular_price and category_name
#using visiondata.json to store title, url, availability, current_price and regular_price
#########################################################################################
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector

from visionsdata.items import Product
from scrapy.loader import ItemLoader
from scrapy.http import Request


class VisionsSpider(CrawlSpider):
    name = "visionsdata"
    domain_name = "visions.ca"
    start_urls = ["http://www.visions.ca/"]

	#speed 
    CONCURRENT_REQUESTS = 15       
    download_delay = 0.3

    rules = (
        # categories   scrapy.linkextractors.LinkExtractor
        Rule(SgmlLinkExtractor(restrict_xpaths=(
            "//li[contains(@class,'menulevel-0')]//div/a",
            "//li[contains(@class,'menulevel-0')]/a[not(contains(./following-sibling::div/@id,'menu')) and contains(@href,'837')]"
            ),
                               unique=True), follow=True),

        #pagination
        Rule(SgmlLinkExtractor(restrict_xpaths=("//a[@title='Next']"),
                               unique=True), follow=True),
        #brands for categories with no sub categories (Gift cards)
        Rule(SgmlLinkExtractor(restrict_xpaths=("//div[contains(@id,'subcatemenu-brand-all')]//a"),
                               unique=True),follow=True),
        #products for bundle and normal categories 
        Rule(
            SgmlLinkExtractor(restrict_xpaths=(
                "//div[contains(@class,'bundleItem')]//td[@class='name']/a",
                "//div[contains(@class,'productresult')]//a[contains(@id,'lnk')]"),
                               unique=True),callback='parse_item', follow=True),
    )

    def parse_item(self,response):
        sel = Selector(response)
		
        #department information
        """
        li=response.xpath("//li[@class='menulevel-0']|//li[@class='menulevel-0 menulevel-0-extra']")
        dName = li.xpath("a/span/text()").extract()
        print dName
		"""
		#category name
        cName = response.xpath("//div/a[2]/text()").extract()[0]
        print ("'Category name' "+ cName)
		#product information
        il = ItemLoader(item=Product(), response=response)
        il.add_xpath("title","//div[contains(@class,'productdetail-container')]//span[contains(@id,'ProdTitle')]/..//text()")
        #il.add_xpath("title","//div[@class='catalogueTitle']/*/text()")   #@class='catalogueTitle'  id='subcatemenu-container'
        il.add_value("url",response.url)
        il.add_xpath("current_price","//div[contains(@class,'pricing') or contains(@class,'price')]//span[contains(@id,'Saleprice') or contains(@class,'salePrice')]//text()")
        il.add_xpath("regular_price","//div[contains(@class,'pricing') or contains(@class,'price')]//span[contains(@id,'Regprice') or contains(@class,'regPrice')]//text()")
        limited = sel.xpath("//div[contains(@id,'FinalClearance')]").extract()
        if len(limited) > 0:
            il.add_value("availability","Limited Quantities")
        else:
            il.add_value("availability","Available")
        return il.load_item()
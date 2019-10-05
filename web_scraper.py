# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request

class SikkoSpider(scrapy.Spider):
    name = 'sikko'
    allowed_domains = ['www.bestbuy.com']
    start_urls = ['https://www.bestbuy.com/site/searchpage.jsp?st=laptops&_dyncharset=UTF-8&id=pcat17071&type=page&sc=Global&cp=1&nrp=&sp=&qp=&list=n&af=true&iht=y&usc=All+Categories&ks=960&keys=keys']

    def start_requests(self):
    	for url in self.start_urls:
    		yield Request(url,callback=self.get_product)

    def get_product(self,response):
    	product_url = response.xpath('//h4[@class = "sku-header"]//a/@href').extract()
    	for i in range(len(product_url)):
    		product_path = response.urljoin(product_url[i].split('.')[0].replace('/site/','/site/reviews/'))
    		print(product_path)
    		yield Request(product_path,callback=self.parse)
    	
    	relative_next_url = response.xpath('//a[@class="ficon-caret-right trans-button "]/@href').extract_first()
    	if relative_next_url:
    		absolute_next_url = response.urljoin(relative_next_url)
    		yield Request(absolute_next_url,callback=self.get_product)
    
    def parse(self, response):
        title = response.xpath('//div[@class="col-xs-12 col-md-9"]//h3[@class="ugc-review-title c-section-title heading-5 v-fw-medium  "]/text()').extract()
        body = response.xpath('//div[@class="col-xs-12 col-md-9"]//p[@class="pre-white-space"]/text()').extract()
        submission_date = response.xpath('//time[@class="submission-date"]/@title').extract()
        recommend_a_friend = response.xpath('//p[@class="v-fw-medium  ugc-recommendation"]/text()').extract()
        rec_friend = [elem.strip() for elem in ' '.join(recommend_a_friend).split('friend') if elem.strip()]
        rec_friend = ['No' if 'No' in elem else 'Yes' for elem in rec_friend]
        helpful = response.xpath('//div[@class="feedback-display"]//button[@data-track="Helpful"]/@aria-label').extract()
        unhelpful = response.xpath('//div[@class="feedback-display"]//button[@data-track="Unhelpful"]/@aria-label').extract()
        product_title = response.xpath('//h2[@class="product-title"]/a[@data-track="Product Description"]/text()').extract()
        rating = response.xpath('//span[@class="c-review-average"]/text()').extract()

        for i in range(len(title)):
            yield {'product title' : product_title , 'title':title[i],'body':body[i],'helpful':helpful[i],'unhelpful':unhelpful[i],'submission date':submission_date[i], 'rating' : rating[i], 'recommend a friend': rec_friend[i]}

        relative_next_url = response.xpath('//a[@data-track = "Page next"]/@href').extract_first()
        if relative_next_url:
            absolute_next_url = response.urljoin(relative_next_url)
            yield Request(absolute_next_url,callback=self.parse)
    	
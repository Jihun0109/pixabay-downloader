# -*- coding: utf-8 -*-
from scrapy import Spider, Request
import re, requests, os

g_types = ['photo','video', 'vector','illustration']

def download(url, destfilename):
	if not os.path.exists(destfilename):
		print ("Downloading from %s to %s..." % (url, destfilename))
		try:
			r = requests.get(url, stream=True)
			with open(destfilename, 'wb') as f:
				for chunk in r.iter_content(chunk_size=1024):
					if chunk:
						f.write(chunk)
						f.flush()
		except:
			print ("Error downloading file.")

class PixabaySpider(Spider):
	name = "pixabay"

	start_urls = [
			"https://pixabay.com/",
	]

	type = "photo"
	keyword = "development"
	thumbnail = False

	
	
	def __init__(self, type='photo', thumbnail=False, *args, **kwargs):
		super(PixabaySpider, self).__init__(*args, **kwargs)
		self.type = type

	def parse(self, response):
		if self.type not in g_types:
			print ("Invalid type: type should be one of 'photo','video', 'vector' and 'illustration'")
			return
			
		base_url = "https://pixabay.com/en/editors_choice/?media_type={}".format(self.type)
		if self.keyword is not "":
			base_url = "https://pixabay.com/images/search/{}/".format(self.keyword)
		yield Request(base_url, self.parse_category)

	def parse_category(self, response):

		target_path = "download/{}/".format(self.type)
		if not os.path.exists(target_path):
			os.makedirs(target_path)
		items = response.xpath('//*[@class="item"]/a')
		print (len(items))
		for item in items:
			if self.type in ["photo","illustration","vector"]:
				src = item.xpath('./img/@src').extract_first()
				if "blank.gif" in src:
					src = item.xpath('./img/@data-lazy').extract_first()
				src = src.replace("__340","_1280")
				
				file_extension = src.split("_1280")[-1]
				file_name = src.split("/")[-1].split("_")[0] + file_extension				
				
			elif self.type == "video":
				# video_url = "https://pixabay.com/en/videos/download/video-7328_large.mp4?attachment"
				link = item.xpath('./@href').extract_first()
				print (link)
				id = link.split("-")[-1].replace('/','')
				src = "https://pixabay.com/en/videos/download/video-{}_large.mp4?attachment".format(id)
				file_extension = ".mp4"
				file_name = id + file_extension

			download(src, target_path+file_name)

			
		next_link = response.xpath('//*[@class="pure-button"]/@href').extract()
		print (next_link)
		if len(next_link) > 1:
			yield Request(response.urljoin(next_link[-1]), self.parse_category)

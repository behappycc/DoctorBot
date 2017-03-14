import requests
from lxml import etree

class DivisionCrawler(object):
	def __init__(self):
		self.division = []
	
	def crawl_search_result(self):
		url = "https://www.ntuh.gov.tw/MedicalTeams/%E9%86%AB%E5%B8%AB%E6%9F%A5%E8%A9%A2_table.aspx"
		r = requests.get(url)
		html = r.content.decode('utf-8')
		page = etree.HTML(html)
		
		res=[]
		for division in page.xpath("//tr"):
        		res.append(division.xpath(".//text()"))
		return res

def main():
	dc = DivisionCrawler()
	dc.crawl_search_result()

if __name__== '__main__':
	main()

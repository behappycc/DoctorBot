import requests
url = "https://www.ntuh.gov.tw/MedicalTeams/%E9%86%AB%E5%B8%AB%E6%9F%A5%E8%A9%A2_table.aspx"
r = requests.get(url)
html = r.content.decode('utf-8')
from lxml import etree
page = etree.HTML(html)
res=[]
for division in page.xpath("//tr"):
        res.append(division.xpath(".//text()"))
import csv
f = open("division.csv","w")  
w = csv.writer(f)  
w.writerows(res)  
f.close() 

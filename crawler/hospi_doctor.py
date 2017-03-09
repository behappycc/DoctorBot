import sys
name = sys.argv[1]
import requests
url = "https://reg.ntuh.gov.tw/webadministration/DoctorServiceQueryByDrName.aspx?HospCode=T0&QueryName=" + name
r = requests.get(url)
html = r.content.decode('utf-8')
from lxml import etree
page = etree.HTML(html)
res=[]
for index,division in enumerate(page.xpath("//table[@id='DoctorServiceListInSeveralDaysInput_GridViewDoctorServiceList']//tr")):
        if index == 0:
            res.append(division.xpath(".//th//text()"))
        else:
            res.append(division.xpath(".//td//span//text()"))
import csv
f = open("doctor.csv","w")  
w = csv.writer(f)  
w.writerows(res)  
f.close() 

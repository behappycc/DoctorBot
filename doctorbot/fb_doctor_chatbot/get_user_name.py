import requests
import re
import urllib
from lxml import etree
from urllib.request import urlopen
from bs4 import BeautifulSoup
import sys
import csv
#name = sys.argv[1]
#2017_3
def get_user_name(id):
	id = 100002571562942 

	url = "https://www.facebook.com/profile.php?id="+str(id)
	html = urlopen(url)
	soup = BeautifulSoup(html.read(), "lxml")
	name = soup.find(id = "pageTitle")
	name = name.contents
	name = name[0].split(' |')[0]
	return name
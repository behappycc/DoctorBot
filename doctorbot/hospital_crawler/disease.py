
# coding: utf-8

# In[1]:

import requests
from bs4 import BeautifulSoup
import os
import codecs

if os.path.exists("disease.csv"):
    os.remove("disease.csv")

res = requests.get("https://health.udn.com/disease/disease_list")
soup = BeautifulSoup(res.text)
body = soup.select('#diagnosis_body')
#print body
#print type(body[0])
#print body[0].attrs
bodytext = str(body)
#print bodytext
start = 0
print "disease number: " + str(bodytext.count("/disease/sole/"))
outfile = codecs.open("disease.csv",'w','utf-8')
outfile.write(unicode(codecs.BOM_UTF8, 'utf-8'))
#outfile.write('疾病名稱,英文名稱,就診科別,身體部位,症狀\n')
def subPage(href):
    print href
    subres = requests.get(href)
    subres.encoding = 'utf-8'
    output = []
    subsoup = BeautifulSoup(subres.text)
    story = subsoup.select('#story_art_title')
    story_name = story[0].text[:len(story[0].text)-10]
    print story_name
    output.append(story_name)
    #card = subsoup.select('.disease_cards')
    card = subsoup.select('ul')
    #print card[0]
    for item in card[0].select('li'):
        title = item.select('span')[0]
        content = item.select('h3')[0]
        print title.text, content.text
        if content.text.find(',') > 0:
            text = ' '.join(content.text.split(','))
            output.append(text)
        else:
            output.append(content.text)
    section = subsoup.select('section')
    print section[0].select('h4')[1].text
    sympton = section[0].select('h4')[1].findNext('p').text
    print sympton
    output.append(sympton)
    try:
        outfile.write(','.join(output)+"\n")
    except:
        print "exception!!!!!"
        outfile.close()
for i in range(bodytext.count("/disease/sole/")):
#for i in range(5):
    indexStart = bodytext.find("/disease/sole/", start)
    indexEnd = bodytext.find('">', indexStart)
    href = "https://health.udn.com" + bodytext[indexStart:indexEnd]
    #print href
    start = indexEnd + 2
    subPage(href)

outfile.close()
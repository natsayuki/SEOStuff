from googlesearch import search
from bs4 import BeautifulSoup as BS
import requests
import math
import os
from collections import Counter

def prop(oldValue, oldMin, oldMax, newMin, newMax):
    return (((oldValue - oldMin) * (newMax - newMin)) / (oldMax - oldMin)) +  newMin

def fetchSites(term):
    num = 20
    pause = 5
    stop = 50
    return search(term, num=num, pause=pause, stop=stop)

def compileWebsites(terms):
    for index, term in enumerate(terms):
        data = fetchSites(term)
        per = (index/len(terms))*100
        print(str(per)+ "% complete [" + ("#" * int(prop(per, 0, 100, 0, 20)))  + (" " * (20 - int(prop(per, 0, 100, 0, 20)))) + "]")
        os.mkdir('websites/'+term)
        with open('websites/'+term+'/'+term+'.websites', 'w+') as f:
            for i, point in enumerate(data):
                # per = index * (i/len(data)) * 100
                # print(str(per)  +"% complete" + ("#" * math.ceil(per/100))  + (" " * (20 - math.ceil(per/100))) + "]")
                f.write(point + '\n')
    print("100% complete [####################]")

def getHTML(term):
    with open("websites/"+term+'/'+term+".websites") as f:
        data = f.readlines()
        for line in data:
            try:
                URL = line.replace('\n', '')
                site = requests.get(URL)
                soup = BS(site.text, 'html.parser')
                count = Counter([tag.name for tag in soup.findAll()])
                file = URL
                for char in '/:.?&=':
                    file = file.replace(char,'')
                string = ''
                for tag in count:
                    string += (tag + ',' + str(count[tag]) + '\n')
                with open("websites/"+term+"/"+file+".csv", "w+") as f:
                    print(string)
                    f.write(string)
            except:
                None

# TODO
# ping
# keywords in page and url
# Date written
# SSL


searchTerms = ["Barack Obama", "Pizza", "Computers", "Baseball", "Alexa", "SEO", "Twitter", "potato", "steak", "building", "sweet potato", "mashed potato", "pokemon fled", "cat", "spicy", "projector"]



# compileWebsites(searchTerms)
getHTML("potato")
print('done')

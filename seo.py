from googlesearch import search
from bs4 import BeautifulSoup as BS
import requests
import math
import os
import json
import re
import random
from collections import Counter

def prop(oldValue, oldMin, oldMax, newMin, newMax):
    return (((oldValue - oldMin) * (newMax - newMin)) / (oldMax - oldMin)) +  newMin

def fetchSites(term):
    num = 25
    pause = 30
    stop = 25
    return search(term, num=num, pause=pause, stop=stop)

def compileWebsites(terms):
    for index, term in enumerate(terms):
        data = fetchSites(term)
        per = (index/len(terms))*100
        print(str(per)+ "% complete [" + ("#" * int(prop(per, 0, 100, 0, 20)))  + (" " * (20 - int(prop(per, 0, 100, 0, 20)))) + "]")
        try:
            os.mkdir('websites/'+term)
        except:
            None
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
                ping = requests.get(URL).elapsed.total_seconds()
                site = requests.get(URL)
                soup = BS(site.text, 'html.parser')
                tags = soup.findAll()
                count = Counter([tag.name for tag in tags])
                titleTags = soup.findAll('title')
                keywordsInTitle = []
                for title in titleTags:
                    keywordsInTitle.append(title.contents[0].lower().find(term.lower()))
                keywordInURL = URL.lower().find(term.lower().replace(" ",""))
                keywordsInBody = [s.start() for s in re.finditer(term.lower(), site.text.lower())]
                file = URL
                obj = {}
                SSL = URL.startswith('https')
                robotsURL = URL + '/robots.txt'
                robotsFile = requests.get(robotsURL)
                robots = False
                if robotsFile.status_code == 200:
                    robots = True
                errors = json.loads(requests.get("https://validator.nu/?doc="+URL+"&out=json").text)
                obj['tags'] = count
                obj['ping'] = ping
                obj['ssl'] = SSL
                obj['termsInTitle'] = keywordsInTitle
                obj['termInUrl'] = keywordInURL
                obj['termsInPage'] = keywordsInBody
                obj['url'] = URL
                obj['robots'] = True
                obj['errors'] = len(errors['messages'])
                for char in '/:.?&=':
                    file = file.replace(char,'')
                with open("websites/"+term+"/"+file+".json", "w") as f:
                    print("websites/"+term+"/"+file+".json")
                    f.write(json.dumps(obj))
            except:
                pass

def compileHTML(terms):
    for term in terms:
        getHTML(term)

def generateSearchTerms(amnt):
    terms = []
    with open('nouns.json') as f:
        nouns = json.load(f)
        for i in range(amnt):
            terms.append(nouns[random.randint(0, len(nouns))])
    with open('terms.json', 'w+') as f:
        json.dump(terms, f)
    return terms

def convertTagsToCSV(term):
    try:
        with open("websites/"+term+"/"+term+".websites") as f:
            for line in f.readlines():
                for char in '/:.?&=\n':
                    line = line.replace(char,'')
                with open("websites/"+term+"/"+line+".json") as f:
                    data = json.load(f)
                    csvString = ""
                    for tag in data['tags']:
                        csvString += tag + ',' + str(data['tags'][tag]) + '\n'
                    with open("websites/"+term+"/"+line+".csv", "w+") as f:
                        print("websites/"+term+"/"+line+".csv")
                        f.write(csvString)
    except:
        None

def compileTagsToCSV(terms):
    for term in terms:
        convertTagsToCSV(term)

def combineCSV(terms):
    total = ""
    for term in terms:
        with open("websites/"+term+"/"+term+".websites") as f:
            for line in f.readlines():
                try:
                    for char in '/:.?&=\n':
                        line = line.replace(char,'')
                    with open("websites/"+term+"/"+line+".json") as f:
                        data = json.load(f)
                        csvLine = data['url']+'~'+str(data['tags'])+'~'+str(data['ping'])+'~'+str(data['ssl'])+'~'+str(data['robots'])+'~'+str(data['errors'])+'~'+str(data['termInUrl'])+'~'+str(data['termsInTitle'])+'~'+str(data['termsInPage'])+'\n'
                        total += csvLine
                        with open("websites/total.csv", "a") as f:
                            f.write(csvLine)
                except:
                    None

def combineJSON(terms):
    total = {}
    for term in terms:
        with open("websites/"+term+"/"+term+".websites") as f:
            for index, url in enumerate(f.readlines()):
                try:
                    line = url
                    for char in '/:.?&=\n':
                        line = line.replace(char,'')
                    with open("websites/"+term+"/"+line+".json") as g:
                        data = json.load(g)
                        data['term'] = term
                        data['rank'] = index
                        data['robots'] = 1 if data['robots'] else 0
                        data['ssl'] = 1 if data['ssl'] else 0
                        data['termsInTitle'] = len(data['termsInTitle'])
                        data['termsInPage'] = len(data['termsInPage'])
                    total[data['url']] = data
                except:
                    None
    with open("websites/total.json", "a") as f:
        json.dump(total, f)

# TODO
# Date written
# Syntax errors
# Meta

# "Barack Obama", "Pizza", "Computers", "Baseball", "Alexa", "SEO", "Twitter", "potato", "steak", "building", "sweet potato", "mashed potato", "pokemon fled", "cat", "spicy", "projector"

searchTerms = []
with open("terms.json") as f:
    searchTerms = json.load(f)

########## REDO BEING, guess, ear, physical, floor, gas

# searchTerms = ["garage", "carpet", "fish", "permit", "shock", "tour", "lip", "combine", "entertainment", "milk", "sock", "prize", "few", "bird", "actor", "expert", "crew", "emotion", "role", "march"]



# compileWebsites(searchTerms)
# compileHTML(searchTerms)
# getHTML('actor')
# compileTagsToCSV(searchTerms)
# combineCSV(searchTerms)
combineJSON(searchTerms)
print('done')

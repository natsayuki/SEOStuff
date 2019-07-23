from googlesearch import search
from bs4 import BeautifulSoup as BS
import requests
import math
import os
import json
import re
import random
from os import walk
from collections import Counter

def prop(oldValue, oldMin, oldMax, newMin, newMax):
    return (((oldValue - oldMin) * (newMax - newMin)) / (oldMax - oldMin)) +  newMin

def fetchSites(term):
    num = 25
    pause = 30
    stop = 25
    return search(term, num=num, pause=pause, stop=stop)

def compileWebsites(terms):
    try:
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
    except:
        None
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
                for char in '/:. if&=\n':
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
    with open('terms.json', 'w') as f:
        json.dump(terms, f)
    return terms

def convertTagsToCSV(term):
    try:
        with open("websites/"+term+"/"+term+".websites") as f:
            for line in f.readlines():
                for char in '/:. if&=\n\n':
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
    with open("websites/total.csv", "w") as f:
        f.write("")
    for term in terms:
        # if term in ignore:
        #     pass
        with open("websites/"+term+"/"+term+".websites") as f:
            for index, line in enumerate(f.readlines()):
                try:
                    for char in '/:. if&=\n':
                        line = line.replace(char,'')
                    with open("websites/"+term+"/"+line+".json") as f:
                        data = json.load(f)
                        data['term'] = term
                        data['rank'] = index
                        data['robots'] = 1 if data['robots'] else 0
                        data['ssl'] = 1 if data['ssl'] else 0
                        data['termsInTitle'] = len(data['termsInTitle'])
                        data['termsInPage'] = len(data['termsInPage'])

                        tags = data['tags']
                        data['h1'] = tags['h1'] if 'h1' in tags else 0
                        data['meta'] = tags['meta'] if 'meta' in tags else 0
                        data['script'] = tags['script'] if 'script' in tags else 0
                        data['img'] = tags['img'] if 'img' in tags else 0
                        data['iframe'] = tags['iframe'] if 'iframe' in tags else 0
                        data['video'] = tags['video'] if 'video' in tags else 0
                        data['p'] = tags['p'] if 'p' in tags else 0
                        data['link'] = tags['link'] if 'link' in tags else 0
                        data['a'] = tags['a'] if 'a' in tags else 0
                        csvLine = data['url']+'~'+str(data['tags'])+'~'+str(data['ping'])+'~'+str(data['ssl'])+'~'+str(data['robots'])+'~'+str(data['errors'])+'~'+str(data['termInUrl'])+'~'+str(data['termsInTitle'])+'~'+str(data['termsInPage'])+'~'+str(data['term'])+'~'+str(data['h1'])+'~'+str(data['meta'])+'~'+str(data['script'])+'~'+str(data['img'])+'~'+str(data['iframe'])+'~'+str(data['video'])+'~'+str(data['p'])+'~'+str(data['link'])+'~'+str(data['a'])+'~'+str(data['rank'])+'\n'
                        total += csvLine
                        with open("websites/total.csv", "a") as f:
                            f.write(csvLine)
                except:
                    None

ignore = ["reason", "warning", "answer", "condition", "scratch", "reputation", "command", "potential", "pot", "manager", "purpose", "pressure", "card", "guy", "proof", "wrap", "spite", "being", "guess", "care", "obligation", "war", "army", "earth", "child", "show", "register", "reputation", "pull", "pause", "line", "surprise", "theme", "brave", "garage", "loss", "cycle", "period", "wear", "pack", "audience", "ear", "business", "basis", "second", "depression", "mode", "community", "distance", "harm", "spare", "business", "confidence", "spot", "professor", "block", "particular", "nothing", "taste", "quiet", "equal", "look", "offer", "brown", "physical", "head", "doubt", "year", "excitement", "report", "pie", "bend", "top", "contract", "opinion", "classic", "floor", "leg", "session", "gas", "garage", "carpet", "fish", "permit", "shock", "tour", "lip", "combine", "entertainment", "milk", "sock", "prize", "few", "bird", "actor", "expert", "crew", "emotion", "role", "march"]

def combineJSON(terms):
    total = {}
    totalTags = {}
    for ui, term in enumerate(terms):
        print(terms)
        with open("websites/"+term+"/"+term+".websites") as f:
            for index, url in enumerate(f.readlines()):
                print(ui * index)
                try:
                    line = url
                    for char in '/:. if&=\n':
                        line = line.replace(char,'')
                    with open("websites/"+term+"/"+line+".json") as g:
                        data = json.load(g)
                        data['term'] = term
                        data['robots'] = 1 if data['robots'] else 0
                        data['ssl'] = 1 if data['ssl'] else 0
                        data['termsInTitle'] = len(data['termsInTitle'])
                        data['termsInPage'] = len(data['termsInPage'])
                        data['rank'] = index
                        tags = data['tags']
                        data['h1'] = tags['h1'] if 'h1' in tags else 0
                        data['meta'] = tags['meta'] if 'meta' in tags else 0
                        data['script'] = tags['script'] if 'script' in tags else 0
                        data['img'] = tags['img'] if 'img' in tags else 0
                        data['iframe'] = tags['iframe'] if 'iframe' in tags else 0
                        data['video'] = tags['video'] if 'video' in tags else 0
                        data['p'] = tags['p'] if 'p' in tags else 0
                        data['link'] = tags['link'] if 'link' in tags else 0
                        data['a'] = tags['a'] if 'a' in tags else 0
                    # totalTags[data['url']] = totalTagsTemp
                    total[data['url']] = data
                except:
                    None
    with open("websites/total.json", "w") as f:
        json.dump(total, f)
    with open("websites/totaltags.json", "w") as f:
        json.dump(totalTags, f)

# TODO
# Meta
# Images

# "Barack Obama", "Pizza", "Computers", "Baseball", "Alexa", "SEO", "Twitter", "potato", "steak", "building", "sweet potato", "mashed potato", "pokemon fled", "cat", "spicy", "projector"

searchTerms = []
try:
    with open("terms.json") as f:
        searchTerms = json.load(f)
except:
    None



termsasdf  = os.walk('websites')
searchTerms = [x[0][9:] for x in termsasdf][1:]
for term in searchTerms:
    print(term)


########## REDO BEING, guess, ear, physical, floor, gas

# searchTerms = ["garage", "carpet", "fish", "permit", "shock", "tour", "lip", "combine", "entertainment", "milk", "sock", "prize", "few", "bird", "actor", "expert", "crew", "emotion", "role", "march"]



# compileWebsites(searchTerms)
# compileHTML(searchTerms)
# getHTML('actor')
# compileTagsToCSV(searchTerms)
# combineCSV(searchTerms)
combineJSON(searchTerms)
# generateSearchTerms(100)
print('done')

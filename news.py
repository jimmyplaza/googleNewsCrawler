# -*- coding: utf-8 -*-
import string
import datetime
import hashlib

from pymongo import MongoClient
import pymongo
import requests
import newspaper
from bs4 import BeautifulSoup
import nltk
import json

#import sys
#import aiohttp
#import asyncio

from util.elk import Elastic
from tf_idf import tfidfRun


source_url = None
elk_host = None
elk_port = None
elk_index = None
elk_type = None
elk_type2 = None
mongo_host = None
mongo_port = None
searchword_config = None
keyWordNum = None
tfidf_flag = None


def main():
    loadConfig()
    with open(searchword_config, 'r') as file:
        for line in file:
            line = line.rstrip('\n')
            print("Search keywords: {}".format(line))
            newsCrawler(line)
    if tfidf_flag:
        print ("-------------- Run tfidf ---------------")
        tfidfRun()

def loadConfig():
    with open("config.json", "r") as con:
        config = json.load(con)
    global source_url
    global elk_host
    global elk_port
    global elk_index
    global elk_type
    global elk_type2
    global mongo_host
    global mongo_port
    global searchword_config
    global keyWordNum
    global tfidf_flag

    source_url = config['source_url']
    elk_host = config['elk_host']
    elk_port = int(config['elk_port'])
    elk_index = config['elk_index']
    elk_type = config['elk_type']
    elk_type2 = config['elk_type2']
    mongo_host = config['mongo_host']
    mongo_port = int(config['mongo_port'])
    searchword_config = config['searchword_config']
    keyWordNum = int(config['keyWordNum'])
    tfidf_flag = int(config['tfidf_flag'])

def strTrim(s):
    table = s.maketrans(string.punctuation, ' '*len(string.punctuation))
    out =  s.translate(table)
    return out

def analysisUrl(db, elk, search, news_url):
    #a = yield from newspaper.Article(news_url)
    a = newspaper.Article(news_url)
    try:
        a.download()
        a.parse()
    except:
        print('parse error')
        return
    print (a.authors)
    print (a.publish_date)
    a.nlp()
    print (a.keywords)
    print (a.title)
    title = strTrim(a.title)
    m = hashlib.md5()
    m.update(title.encode('utf-8'))
    m.update(str(a.publish_date).encode('utf-8'))
    hashId = m.hexdigest()
    print (hashId)
    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d")
    article = {
            "text": a.text,
            "keywords": a.keywords,
            "publish_date": a.publish_date,
            "author": a.authors,
            "url": news_url,
            "title": a.title,
            "searchword": search,
            "date": date,
    }

    try:
        db.news.update({'aid':hashId},{'$setOnInsert':article},upsert=True)
        print("Save to MongoDB")
    except pymongo.errors.PyMongoError as e:
        print("MongoDB error: %s " % e )
    elk.save2elk(elk_index, elk_type, hashId, article)

def newsCrawler(search):
    url = source_url % (search)
    res = requests.get(url)
    soup = BeautifulSoup(res.text,"lxml")
    client = MongoClient(mongo_host, mongo_port)
    db = client['news']
    nltk.download('punkt')
    elk = Elastic(elk_host, elk_port)
    urlArr = []

    for item in soup.select(".esc-body"):
        news_title = item.select(".esc-lead-article-title")[0].text
        news_url = item.select(".esc-lead-article-title")[0].find('a')['href']
        print ('news_title: ' + news_title)
        print ('news_url: ' + news_url)
        urlArr.append(news_url)
    print("===================")
    print(urlArr)
    #tasks = [analysisUrl(search, u) for u in urlArr]
    #asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))

    count = 1
    for u in urlArr:
        print ('======[',count,']=========')
        analysisUrl(db, elk, search, u)
        count += 1



if __name__=="__main__":
    main()







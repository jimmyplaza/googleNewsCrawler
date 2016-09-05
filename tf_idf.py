# -*- coding: utf-8 -*-
import sys
import datetime
import json

from pymongo import MongoClient
from util.tfidf import TfIdf
from util.elk import Elastic

keyWordNum = None
elk_host = None
elk_port = None
elk_index = None
elk_type = None
elk_type2 = None
mongo_host = None
mongo_port = None

def loadConfig():
    with open("config.json", "r") as con:
        config = json.load(con)
    global elk_host
    global elk_port
    global elk_index
    global elk_type
    global elk_type2
    global mongo_host
    global mongo_port
    global keyWordNum

    elk_host = config['elk_host']
    elk_port = int(config['elk_port'])
    elk_index = config['elk_index']
    elk_type = config['elk_type']
    elk_type2 = config['elk_type2']
    mongo_host = config['mongo_host']
    mongo_port = int(config['mongo_port'])
    keyWordNum = int(config['keyWordNum'])

def tfidfRun():
    """
    Calcuate the tfidf of today's news at MongoDB, input the keywords to elk.
    """
    loadConfig()
    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d")
    print(date)

    client = MongoClient(mongo_host, mongo_port)
    elk = Elastic(elk_host, elk_port)
    db = client['news']
    cursor = db.news.find({"date": date});
    print ("article count: %d" % cursor.count())
    if cursor.count() == 0:
        print ('Today %s has no data to analysis.' % (date))
        sys.exit(0)
    article = cursor[:]

    corpus = []
    mapping = {}
    mappingUrl = {}
    i = 0
    for row in article:
        text = row['text']
        corpus.append(text)
        mapping[i] = row['aid']
        mappingUrl[i] = row['url']
        i = i + 1

    tfi = TfIdf(corpus, keyWordNum)
    tfi.tfidf()
    keywordsArr = tfi.keywordsArr
    wordsArr = tfi.wordsArr

    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d")
    for n, json_data in enumerate(keywordsArr):
        jbody= {"doc":{"tfidf": json_data}}
        wordbody = {
            "date": date,
            "url": mappingUrl[n],
            "word": wordsArr[n]
        }
        elk.update2elk(elk_index, elk_type, mapping[n], jbody)
        elk.save2elk(elk_index, elk_type2, mapping[n], wordbody)

    print("\nComplete!")

if __name__=="__main__":
    tfidfRun()



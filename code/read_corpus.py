#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  1 17:33:53 2018

@author: alaa
"""

from pymongo import MongoClient
import pandas as pd 

client =  MongoClient()
db1 = client.CrawlingInfo
last_crawling_col = db1.last_crawling.find({'crawl': True})
for last_crawling_rec in last_crawling_col:
    db = client['annotation_'+ str(last_crawling_rec['_id'])]
    corpus = db.corpus.find({}, {'body':1, 'answer':1, 
                                 'accountName':1, 'UserName':1})

for coll in corpus:
    df = pd.DataFrame.from_dict(coll)
    df.to_csv('corpus.csv', index=False)
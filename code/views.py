# -*- coding: utf-8 -*-
"""
Created on Sun Jul 22 15:04:31 2018

@author: alaa
"""

from flask import Flask, request
from pymongo.collection import ReturnDocument
from pymongo import MongoClient
import datetime

app = Flask(__name__)

@app.route('/twitterCrawler/api/v1.0', methods=['POST', 'GET'])        
def twitterCrawling():
    """API flask function
       url = 'http://localhost:5008/twitterCrawler/api/v1.0'
       args = action, projectId, accountName
    """
    # the parameters should be called first as they will be extracted from the request header
    action = request.args['action']
    projectId = request.args['projectId']
    accountName =  request.args['accountName'] 
    if accountName != None and projectId != None and action != None:
        """check if the account name in the last crawling database 
       if its not there insert it with lastCrawlingDate (4-years ago)
       if its there return"""
        client = MongoClient()
        db1 = client.CrawlingInfo
        last_crawling_date_from_4_yrs = (datetime.datetime.now() - datetime.timedelta(days=4*365)).strftime('%Y-%m-%d %H:%M:%S')
        profileUrl = db1.last_crawling.find_one({'_id': projectId})
        if profileUrl == None or profileUrl['accountName'] != accountName: # not inserted
            # this maybe duplicate
            db1.last_crawling.insert_one({'accountName': accountName,
                                          'lastCrawlingDate': last_crawling_date_from_4_yrs,
                                          '_id': projectId, 'crawl':True})
            return "New Account"
        
        if profileUrl != None:
            if action != "start" : # already inserted
                updated_document1 = db1.last_crawling.find_one_and_update(
                                    filter = {'_id': projectId}, 
                                    update = {'$set': {'crawl': False}},
                                    return_document=ReturnDocument.AFTER)
                return str(updated_document1['lastCrawlingDate'])
                
            if profileUrl['crawl'] == False and action == 'start':
                updated_document3 = db1.last_crawling.find_one_and_update(
                                    filter = {'_id': projectId}, 
                                    update = {'$set': {'crawl': True}},
                                    return_document=ReturnDocument.AFTER)
                return str(updated_document3['lastCrawlingDate']), str(updated_document3['accountName'])
    return "Done"
        
if __name__ == '__main__':
    app.run(debug=True, port=5008)
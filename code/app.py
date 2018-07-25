# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 14:19:00 2018

@author: alaa
"""

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from multiprocessing import Process
#from threading import Thread
from pyquery import PyQuery as pq
from lxml import html
from time import sleep
import dateutil.parser
import datetime
import tweepy
import json
import re
from project_template_utilties import init_driver, format_day, form_url, increment_day, close_driver

def update_last_crawling_date():
    """when you crawling ends, update
       current user's last crawlig date to now """
    client =  MongoClient()
    db1 = client.CrawlingInfo
    now_time = datetime.datetime.now()
    lastCrawlingColl = db1.last_crawling.find({}) 
    if lastCrawlingColl != None:
        for lastCrawlingRec in lastCrawlingColl:
#            if lastCrawlingRec['accountName'] == None :
#                db1.last_crawling.insert_one({'_id': lastCrawlingRec['projectId'],
#                                              'accountName': lastCrawlingRec['accountName'],
#                                              'lastCrawlingDate': now_time, 'crawl':True})
            if ((dateutil.parser.parse(lastCrawlingRec['lastCrawlingDate']) - now_time).days + 1) >= 1:
                # should go and start scrawling
                db1.last_crawling.find_one_and_update(filter = {'_id': lastCrawlingRec['projectId']},
                                                      update = {'$set': {'crawl': True}})
            else: # 
                return  
            
def logging(msg, id_):
    """log messages to MongoDB log"""
    client =  MongoClient()
    db1 = client.CrawlingInfo
    last_crawling_col = db1.last_crawling.find()
    for last_crawling_rec in last_crawling_col:
        db = client['annotation_'+ str(last_crawling_rec['_id'])]
        entry = {}
        entry['msg'] = msg
        if id_ == str(last_crawling_rec['_id']):
            db.log_collection.insert_one(entry)
    
def fetch_tweets_ids(days, start, accountName, driver_delay, driver, api, projectId, db1):
    """a function that fetches Ids and its metadata/ json info"""
    # define ids and tweets selectors from page source
    id_selector = '.time a.tweet-timestamp'
    tweet_selector = 'li.js-stream-item'
    ids = []
    c = 0
    for day in range(days):
      d1 = format_day(increment_day(start, 0))
      d2 = format_day(increment_day(start, 1))
      url = form_url(since=d1, until=d2, user=accountName) 
      logging(url, projectId)
      logging('Crawling start date: {}'.format(d1), projectId)
      try:
          driver.get(url)
          sleep(driver_delay)
      except TimeoutException:
          logging('TIMEOUT EXCEPTION', projectId)
          c += 1
          continue
      print("Number of timeout exceptions: {}".format(c))
      try:
          found_tweets = driver.find_elements_by_css_selector(tweet_selector)
          increment = 10
          while len(found_tweets) >= increment:
              logging('scrolling down to load more tweets', projectId)
              driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
              sleep(driver_delay)
              increment += 10
          logging('{} tweets found, {} total ids'.format(len(found_tweets), len(ids)), projectId)
          for tweet in found_tweets:
              try:
                  id = tweet.find_element_by_css_selector(id_selector).get_attribute('href').split('/')[-1]
                  if(id not in ids):
                      ids.append(id)
                  try:
                      tweet_ = api.get_status(id)
                  except tweepy.error.TweepError as e:
                      logging("TWEEP ERROR: {}".format(e.api_code), projectId)
                      continue
                  tweet_json = dict(tweet_._json)
                  if tweet_json["in_reply_to_status_id_str"] != None and tweet_json["in_reply_to_screen_name"] != None:
#                      try:
                      db1.tweets_ids.insert_one({'_id': tweet_json["id_str"], 
                                                 'in_reply_to_status_id_str': tweet_json["in_reply_to_status_id_str"] ,
                                                 'in_reply_to_screen_name': tweet_json["in_reply_to_screen_name"] ,
                                                 'created_at': tweet_json["created_at"],
                                                 'accountName':accountName,
                                                 'projectId': projectId,
                                                 'used': False})
#                      except DuplicateKeyError:
#                            logging("DUPLICATION ERROR!", projectId)
              except StaleElementReferenceException as e:
                  logging('LOST ELEMENT REFRENCE', projectId)                   
          logging(str(len(ids) ) + " -------- IDS IS FETCHED --------", projectId)
      except NoSuchElementException:
          logging('NO TWEETS ON THAT DAY', projectId)
      start = increment_day(start, 1)
    logging('ALL DONE HERE', projectId)
    close_driver(driver)  
      
def tweetsIdsFetcher():
    #write in tweetsIds
    #insert delay
    driver_delay = 1
    delay = 10 # delay between 2 threads= 10 secs
    
    client = MongoClient()
    db1 = client.CrawlingInfo
    lastCrawlingColl = db1.last_crawling.find({'crawl': True})
    if lastCrawlingColl.count() > 0: # if there is something to cawl
        # initiate the chrome driver
        driver = init_driver(browser="chrome") # only sart the driver if there is something to crawl
    else:
        print("THERE IS NO THING TO CRAWL")
        tweetsAndRepliesFetcher() #return, go query other corpus for any of used=false tweets_ids 
    with open('../api_keys/api_keys.json') as f:
      keys = json.load(f)
    # Do authentication to call API
    try:
        auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
        auth.set_access_token(keys['access_token'], keys['access_token_secret'])
        api = tweepy.API(auth)
    except tweepy.error.TweepError:
        print("Twitter API authentication failed!")
        return
    
    # Handle condition when user/ profileUrl is/ is not exsisted in the Mongodb
    while True: # infinite loop that loops the lastCrawling collection
        lastCrawlingColl = db1.last_crawling.find({'crawl': True}) # query profileUrl to specify the crawled account
        if lastCrawlingColl != None:
            for lastCrawlingRecord in lastCrawlingColl:
                
                lastCrawlingDate = lastCrawlingRecord['lastCrawlingDate']
                accountName = lastCrawlingRecord['accountName']
                projectId = lastCrawlingRecord['_id']
                logging("User {} data already existed, It's last crawling date: {}".format(accountName, lastCrawlingDate), projectId)
                start_date = dateutil.parser.parse(lastCrawlingDate).strftime('%b %d %Y')
                end_date = (datetime.datetime.now()).strftime('%b %d %Y')
                start = datetime.datetime.strptime(start_date, '%b %d %Y')
                end = datetime.datetime.strptime(end_date, '%b %d %Y')
                update_last_crawling_date() # call to check if the diff between today's date and last_crawling_date in last_crawling is > 1 day
            
                days = abs((end - start).days) + 1
                logging("{} days will be crawled".format(days) , projectId)
                # call function that will fetch data ids and write metadata in mongodb
                fetch_tweets_ids(days, start, accountName, driver_delay, driver, api, projectId, db1)
        sleep(delay)

def tweetsAndRepliesFetcher():
    #write in corpus
    #insert delay
    driver_delay = 1 # I increased delay, because htmlunit remote driver rises a Read timeout exception and closes the session
    driver = init_driver(browser="htmlunit")
    
    client = MongoClient()
    db1 = client.CrawlingInfo
    tweet_statuses = db1.tweets_ids.find({'used':False})
    if tweet_statuses != None:
        for tweet_status in tweet_statuses:
          db = client['annotation_'+ str(tweet_status['projectId'])]
          if (len(tweet_status) > 1) and (tweet_status['in_reply_to_status_id_str'] != "None") or (tweet_status['in_reply_to_screen_name'] != "None"):
            url = "https://twitter.com/"+tweet_status['accountName']+"/status/"+ tweet_status['_id']
            logging("Conversation URL:{} ".format(url), str(tweet_status['projectId']))
            try:
                driver.get(url)
            except TimeoutException:
                logging('TIMEOUT EXCEPTION', str(tweet_status['projectId']))
                continue
            sleep(driver_delay)
            source = driver.page_source
            source = source.encode("utf-8")
            page = pq(html.fromstring(source)) 
#            first_tweet = ['NULL']
            ques_tweet = []
            answer_tweet = []
            twt_i = 0
            tweet_no = 0
            line_i = 0
          for twt in pq(page('.js-actionable-tweet')):
            tweet_id = pq(twt).attr['data-tweet-id']
            tweet_text = pq(twt)('.js-tweet-text-container').text()
            # Created at of a tweet   
            twt_data = [tweet_id, 
                        pq(twt).attr['data-screen-name'],
                        pq(twt).attr['data-user-id'],
                        str(pq(twt).attr['data-has-parent-tweet']),
                        str(pq(twt).attr['data-associated-tweet-id']),
                        tweet_text]
            
#            if(twt_i == 0 and pq(twt).attr['data-screen-name'] == tweet_status['accountName']):
#                first_tweet = twt_data
            if(tweet_id == tweet_status['_id']):
                answer_tweet = twt_data
                break
            else:
                ques_tweet = twt_data
            twt_i += 1
          if(len(answer_tweet) and len(ques_tweet)):
              logging(str(line_i) + " --Tweet: " + str(tweet_no), str(tweet_status['projectId']))
              line_i += 1
              try:
                  db.corpus.insert_one({
                          '_id': ques_tweet[0], #ques_tweet[0], I think that ques_tweet[0] vontains in_reply_to_status_id_str which represents the original tweet id no the reply tweet id
                          'header' : "",
                          'body': re.sub(r'(?:@[\w_]+)','' , str(ques_tweet[5])),
                          'answer': re.sub(r'(?:@[\w_]+)','' , str(answer_tweet[5])),
                          'UserName': ques_tweet[1],
                          'accountName': tweet_status['accountName'],
                          'annotatedEntities': [],
                          'patternId': "",
                          'type': 3,
                          'deletedTag': 0,
                          'deletedPatternTag': 0,
                          'created': tweet_status['created_at'],
                          'answerResult': 0})           
              except DuplicateKeyError:
                logging("DUPLICATION ERROR!", str(tweet_status['projectId']))
              # after inserting the data, you need to update documents that has replyId = TweetId in tweets_ids
              db1.tweets_ids.find_one_and_update(filter = {'in_reply_to_status_id_str': ques_tweet[0]},
                                                 update = {'$set': {'used': True}})
              db1.last_crawling.find_one_and_update(filter = {'_id': tweet_status['projectId']},
                                                 update = {'$set': {'crawl': False, 'lastCrawlingDate': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}) # stop crawling & updtae lastCrawlingDate to now after fetching first tweet&reply
              
def twitterCrawlingService():
    #on run two processes
     p1 = Process(target = tweetsIdsFetcher())
     p1.start()
     p2 = Process(target = tweetsAndRepliesFetcher())
     p2.start()
     p1.join()
     p2.join()
#    Thread(target = tweetsIdsFetcher).run() #, name="tweetsIdsFetcher"
#    Thread(target = tweetsAndRepliesFetcher).run()#(), name="tweetsAndRepliesFetcher"

if __name__ == '__main__':
    twitterCrawlingService() # you probably would need to comment that if you are on windows and wanna run it as a bg process
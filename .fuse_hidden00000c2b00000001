# twitter_account_crawling_using_selenium
## A project that crawls tweets and their replies of any twitter account using Selenium

To run this project:

1. Run the flask simple app `views.py`, where you must send those 3 parameters (projectId, accountName, action) for example, you can put **projectId**='4', **accountName**='elonmusk' and **action**='start' in the following format in any browser of your choice http://localhost:5008/twitterCrawler/api/v1.0?action=start&accountName=elonmusk&projectId=4
Doing so will add a record in `last_crawling` collection in the `CrawlingInfo` database.

2. Run the selenium standalone server to be able to run the htmlunit driver
I am using 2 drivers (chrome and htmlunit with javascript) the chromedriver is for the stage where we fetch the tweets ids and we need to use a GUI browser for this stage because we depend on selenium's ability infinite scrolling on each search page of twitter account every daty through the specified span, so to do so:
 `java -jar selenium_server&chrome_driver/selenium-server-standalone-3.13.0.jar`  

3. Run the `app.py` script that will start crawling the account tweets, this script has 2 main functions 
	> Fetching replies Ids  `tweetsIdsFetcher()`
	This is responsible for following search links in twitter(the one's you get when using advanced search options) e.g. the link will look like this (this one represents the tweets that @elonmusk tweeted between 2016-07-21 and 2016-07-22):
	https://twitter.com/search?f=tweets&vertical=default&q=from%3Aelonmusk%20since%3A2016-07-21%20until%3A2016-07-22include%3Aretweets&src=typd
	and then selecting the tweets with thte replies and extracting thier ids and other metadata

	> Fetching Tweets and thier replies text `tweetsAndRepliesFetcher()`
	This is responsible for aligning the tweets and their replies in the `corpus` collection in `annotation_projectId` dataset

4. (Optional) to run `app.py` as a Windows background service, you have to run `create_windows_bgprocess.py`. If 
you are on Linux use the following command ```nohup python app.py & ```
### NOTES
- I used [Robo3T](https://robomongo.org/download) as a database management system to keep track of all the collections and databases
- Also, I organized the DB in a way that every **projectId** is used to create the `annotation_projectId` database with 2 collections in it `corpus` and `logging` where corpus contains the tweets in field 'body', replies in field 'answer', creation date
- I used [Postman](https://www.getpostman.com/apps) to send the POST requests with the parameters projectId, accountName and action

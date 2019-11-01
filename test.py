import bs4
import re
import tweepy
from tweepy import OAuthHandler
from newspaper import Article
import nltk
from textblob import TextBlob
import csv

try:
	from googlesearch import search
except ImportError:
	print("No module named 'google' found")

class NewsAndTwitterAnalysis(object):
	def __init__(self):
		with open('data.txt') as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',')
			line_count = 0
			for row in csv_reader:
				try:
					self.auth = OAuthHandler(str(row[0]), str(row[1]))
					self.auth.set_access_token(str(row[2]), str(row[3]))
					self.api = tweepy.API(self.auth)
				except:
					print("Error: Authentication Failed")

	def cleanTweet(self, tweet):
		return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

	def getSentiment(self, tweet):
		analysis = TextBlob(str(tweet))
		return analysis.sentiment.polarity

	def getTweets(self, query, count = 10):
		tweets = []

		try:
			fetchedTweets = self.api.search(q = query, count = count)

			for tweet in fetchedTweets:
				parsedTweet = {}
				parsedTweet['text'] = tweet.text
				parsedTweet['sentiment'] = self.getSentiment(tweet.text)

				if tweet.retweet_count > 0:
					if parsedTweet not in tweets:
						tweets.append(parsedTweet)
				else:
					tweets.append(parsedTweet)
			return tweets
		except tweepy.TweepError as e:
			print("Error : " + str(e))

news_source = input("What news source do you want to analyze: ")
query = input("What do you want to search: ")

def getLink(s):
	for i in search(news_source + " " + query, tld="com", lang="en", num=s+1, start=s, stop=s+1, pause=2):
		return i

def analyzeArticleSentiment():
	con = True
	n = 0
	link = ""
	while(con):
		if "videos" in getLink(n):
			con = True
			n+=1
		else:
			con = False
			link = getLink(n)
	print(link)

	article = Article(link)

	article.download()
	article.parse()
	nltk.download('punkt')
	article.nlp()

	text = article.summary

	print(text)

	obj = TextBlob(text)
	sentiment = obj.sentiment.polarity

	return sentiment

def main():
	api = NewsAndTwitterAnalysis()
	tweets = api.getTweets(query = query, count = 200)
	print("Analysis: " + str(analyzeArticleSentiment()) + " " + str(api.getSentiment(tweets)))

if __name__ == "__main__":
	main()

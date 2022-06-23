import time

import tweepy


class SaigaStream(tweepy.StreamingClient):
    def on_tweet(self, tweet):
        link = "https://twitter.com/twitter/statuses/"


def dictFromFile(filename):
    with open(filename, 'r') as file:
        temp = {}
        for line in file.read().split('\n'):
            line_split = line.split(':=')
            temp[line_split[0]] = line_split[1]
    return temp


api_key_dict = dictFromFile("config/apikeys")

twitter_api_key = api_key_dict["twitter_api_key"]
twitter_api_secret = api_key_dict["twitter_api_secret"]
twitter_access_key = api_key_dict["twitter_access_key"]
twitter_access_secret = api_key_dict["twitter_access_secret"]

twitter_bearer_token = api_key_dict["twitter_bearer_token"]
twitter_stream_account_ids = dictFromFile("config/twitter_stream_account_ids")
twitterStreamRule = ""
for item in twitter_stream_account_ids.keys():
    twitterStreamRule += "from:" + item + " "
twitterStreamRule += "-is:retweet -is:reply -is:quote"
streamClient = SaigaStream(twitter_bearer_token)
streamClient.add_rules(tweepy.StreamRule(twitterStreamRule))
streamClient.filter(threaded=True)


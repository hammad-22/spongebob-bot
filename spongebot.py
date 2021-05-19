import tweepy
import logging
from config import create_api
import time
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

accounts = ["AIPAC", "Israel", "IDF"]
already_answered = []

def memify(text, length):
    if(text.startswith("@", 0)):
        text = text.partition(" ")[2]
    new = []
    s = "..\n\n𝗙𝗥𝗘𝗘 𝗣𝗔𝗟𝗘𝗦𝗧𝗜𝗡𝗘 🇵🇸"
    b = True
    text = f'"{text}"'
    if(len(text)+len(s) < 279):
        for i in range(len(text)):
            c = text[i]
            if b:
                new.append(c.upper())
                b = False
            else:
                new.append(c.lower())
                b = True
        return "".join(new + [s])
    else:
        print("its going here actually")
        for i in range(len(text)-len(s)+length < 279):
            c = text[i]
            if b:
                new.append(c.upper())
                b = False
            else:
                new.append(c.lower())
                b = True
        return "".join(new + [s])


def check_tweets(count, api):
    account = accounts[count]
    tweets = api.user_timeline(screen_name=account)
    for tweet in tweets:
        try:
            api.update_with_media("sponge.jpeg",
                status="@"+tweet.user.screen_name+" " + memify(tweet.text, len(tweet.user.screen_name)),
                in_reply_to_status_id=tweet.id,
            )
        except tweepy.TweepError as error:
            if error.api_code == 187:
                # Do something special
                print('duplicate message')
            else:
                raise error


def check_mentions(api, since_id):
    logger.info("Retrieving mentions")
    new_since_id = since_id
    for tweet in tweepy.Cursor(api.mentions_timeline,
        since_id=since_id).items():
        new_since_id = max(tweet.id, new_since_id)
        try:
            last_tweet = api.get_status(tweet.in_reply_to_status_id_str)
        except:
            last_tweet = tweet
        print("last tweet" + last_tweet.text)
        if last_tweet.id not in already_answered:
            already_answered.append(tweet.id)
            if last_tweet.in_reply_to_status_id is not None:
                continue
            logger.info(f"Answering to {tweet.user.name}")
            try:
                api.update_with_media("sponge.jpeg",
                    status="@"+tweet.user.screen_name+" " + memify(last_tweet.text, len(tweet.user.screen_name)),
                    in_reply_to_status_id=tweet.id,
                )
            except tweepy.TweepError as error:
                if error.api_code == 187:
                    # Do something special
                    print('duplicate message')
                else:
                    raise error
        else:
            logger.info("already tweeted")
    return new_since_id

def main():
    count = 0
    api = create_api()
    since_id = 1
    while True:
        # while count < 3:
        #     logger.info("checking tweets")
        #     check_tweets(count, api)
        #     count = count + 1
        # count = 0
        since_id = check_mentions(api, since_id)
        logger.info("Waiting...")
        time.sleep(15)

if __name__ == "__main__":
    main()
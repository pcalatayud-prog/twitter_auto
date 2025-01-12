# Script Created by: Pablo Calatayud
# Email: pablocalatayudpelayo@gmail.com
# LinkedIn: https://www.linkedin.com/in/pablo-calatayud-pelayo/
# Copyright (c) 2025, Pablo Calatayud. All rights reserved.

import tweepy

from config.auth import api_key
from config.auth import api_key_secret
from config.auth import access_token
from config.auth import access_token_secret
from config.auth import bearer

def post_twitter(text: str):

    client = tweepy.Client(
        bearer_token=bearer,
        consumer_key=api_key,
        consumer_secret=api_key_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )

    message = text
    client.create_tweet(text=message)

    return None


# if __name__ == "__main__":
#     stop=1
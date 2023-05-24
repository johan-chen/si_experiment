import snscrape.modules.twitter as sntwitter
import pandas as pd
import ast
import math
import numpy as np

df_handles = pd.read_csv("top500twitterhandles.csv")
# news_outlets = list(set(df_handles["handles"]))
df_handles["handles"] = df_handles["handles"].apply(lambda x: ast.literal_eval(x))
news_outlets = df_handles["handles"].explode().tolist()
news_outlets = [x for x in news_outlets if str(x) != 'nan']

news_outlets = list(set(news_outlets))
pd.DataFrame(news_outlets, columns=["handle_name"]).to_csv("outlet_handles.csv", index=False)
# news_outlets = news_outlets[~np.isnan(news_outlets)]
df_tweets = pd.DataFrame(columns=['user', 'date', 'hashtags', 'tweet', 'followers_count', 'created', 'verified',
                                          'url', 'reply_count', 'retweet_count', 'quote_count', 'like_count',
                                          'view_count', 'media', 'retweeded_tweet', 'quoted_tweet', 'in_reply_to_user',
                                          'mentioned_users'])
#%%
i = 0
for outlet in news_outlets:
    i += 1
    print(i, "outlet:", outlet)

    query = f"chatgpt (from:{outlet}) lang:en until:2023-03-01 since:2022-11-30"
    tweets = []

    for tweet in sntwitter.TwitterSearchScraper(query).get_items():
        tweets.append([tweet.user.username, tweet.date, tweet.hashtags, tweet.content, tweet.user.followersCount, tweet.user.created, tweet.user.verified,
                       tweet.url, tweet.replyCount, tweet.retweetCount, tweet.quoteCount, tweet.likeCount,
                       tweet.viewCount, tweet.media, tweet.retweetedTweet, tweet.quotedTweet, tweet.inReplyToUser,
                       tweet.mentionedUsers])

    df_tweets = pd.concat([df_tweets, pd.DataFrame(tweets, columns=df_tweets.columns)], ignore_index=True)

df_tweets.to_csv("tweets_outlets.csv", index=False)
print("done")




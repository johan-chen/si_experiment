import pandas as pd
import numpy as np
import re
import ast

df_tweets = pd.read_csv("tweets_outlets.csv")
df_slant = pd.read_csv("top500twitterhandles.csv")
# Define the pattern to match
pattern = re.compile(r"https://t.co/\w+")

df_t = df_tweets
df_t['tw_content'] = df_t['tweet']
df_t['tw_content'] = df_t['tw_content'].apply(lambda x: re.sub(pattern, '', x))
df_t = df_tweets.groupby('user').apply(lambda x: x.drop_duplicates(subset=['tw_content']))
df_t = df_t.reset_index(drop=True)
df_t["user"] = df_t["user"].str.lower()

df_s = df_slant
df_s["handles"] = df_s["handles"].apply(lambda x: ast.literal_eval(x))
df_s = df_s.explode('handles')
df_s = df_s.reset_index(drop=True)
# df_s = df_s.dropna(subset='handles')
df_s['handles'] = df_s['handles'].astype(str).apply(lambda x: re.sub('@', '', x))
#%%
# Which handles appear more than once?
df_multi_tw = df_s[df_s['handles'] != '[]']
df_multi_tw = df_multi_tw.groupby('handles').filter(lambda x: len(x) > 1)
#%%
# add www. to gizmodo for the next step
df_s['domain'] = df_s['domain'].replace("gizmodo.com", "www.gizmodo.com")

def remove_duplicate_handles(df):
    m_handles = df["handles"].value_counts()[df["handles"].value_counts() > 1].index
    # m_handles = m_handles.drop('[]')
    for handle in m_handles:
        df_handle = df[df['handles'] == handle]
        i = 0
        while i < df_handle.shape[0]:
            # print(df_handle.index[i])
            if df['domain'].iloc[df_handle.index[i]].startswith('www.') and \
                    df['domain'].iloc[df_handle.index[i]].endswith('.com'):
                df.loc[df_handle.index[i], 'handles'] = handle
            elif df['domain'].iloc[df_handle.index[i]].startswith('www.') and \
                    df['domain'].iloc[df_handle.index[i]].endswith('.gov'):
                df.loc[df_handle.index[i], 'handles'] = handle
            else:
                # print(df.iloc[df_handle.index[i]])
                df.loc[df_handle.index[i], 'handles'] = np.nan
            i += 1
    df['handles'] = df['handles'].replace(np.nan, "[]")
    return df

df_s = remove_duplicate_handles(df_s)

#%%
df = pd.merge(df_t, df_s, how="left", left_on="user", right_on="handles")

#%%
#########################################
# Calculate Sentiments for tweets
#########################################
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()
df["vader_sentiment"] = df["tw_content"].apply(lambda x: analyzer.polarity_scores(x))

df['negative_sentiment'] = df['vader_sentiment'].apply(lambda x: x['neg']).groupby(df['user']).transform('mean')
df['neutral_sentiment'] = df['vader_sentiment'].apply(lambda x: x['neu']).groupby(df['user']).transform('mean')
df['positive_sentiment'] = df['vader_sentiment'].apply(lambda x: x['pos']).groupby(df['user']).transform('mean')
df['compound_sentiment'] = df['vader_sentiment'].apply(lambda x: x['compound']).groupby(df['user']).transform('mean')

df_sentiment = df.groupby("avg_align", as_index=False).first()


#%%
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(8,6))

senti = "negative_sentiment"
# todo removed dailydot as outlier because it is only one tweet expressing sarcasm
# todo check all one tweet if sarcasm etc -> remove outlet
df_senti = df_sentiment[df_sentiment.handles != 'dailydot']
df_senti = df_senti.reset_index(drop=True)
x = df_senti["avg_align"]
y = df_senti[senti]
w = df_senti["followers_count"]
l = df_senti["user"]
w_pow = np.power(w, 0.5)
x_axis_cond = x > 0

ax.scatter(x, y, s=300*w_pow/np.max(w_pow), alpha=0.2, label='Aggr. tweets per outlet (size according to # followers)')
for i in range(len(x)):
    label = l
    if w[i] > 15000000:
        plt.annotate(label[i], xy=(x[i], y[i]), xytext=(x[i]+0.06, y[i]+0.005),
                     arrowprops=dict(arrowstyle="-", connectionstyle="arc3, rad=0.3"))
# ax.scatter(x[x_axis_cond], y[x_axis_cond], s=w_log[x_axis_cond], color='#E81B23')
# ax.scatter(x[~x_axis_cond], y[~x_axis_cond], s=w_log[~x_axis_cond], color='#0000ff')
# ax.scatter(x,y, color='k')
# plt.axhline(y=0, color='k', linestyle='-')
## Set background to red/blue
# plt.axvspan(0,1, alpha=0.15, color='r')
# plt.axvspan(-1,0, alpha=0.15, color='b')
# ax.set_title("Mean negative sentiment of tweets about ChatGPT by news outlets")
ax.set_xlabel("Ideological slant")
ax.set_ylabel("Mean negative sentiment towards ChatGPT")
ax.legend()
# fit linear regression with Least squares
b,a = np.polyfit(x, y, deg=1, w=w_pow)

ax.plot(x,a + b*x, alpha=0.5)#, color='k')
fig.savefig('chatgpt/'+ senti + '_slant_w.png')
plt.show()
#%%
w_pow = pd.DataFrame({
    'followers': w,
    '0.1': np.power(w, 0.1),
    '0.2': np.power(w, 0.2),
    '0.3': np.power(w, 0.3)
})

#%%

import seaborn as sns

fig, ax = plt.subplots(figsize=(10,8))

# first_cols = df.loc[:, :'view_count']
# last_cols = df.loc[:, 'avg_align':]
# corr_matrix = pd.concat([first_cols, last_cols], axis=1).corr()
first_cols = df_sentiment.loc[:, 'avg_align':'followers_count']
last_cols = df_sentiment.loc[:, 'negative_sentiment':]
corr_matrix = pd.concat([first_cols, last_cols], axis=1).corr()
sns.heatmap(corr_matrix, annot=True)
plt.tight_layout()
fig.savefig('chatgpt/correlation_sentiment_slant.png')
plt.show()

#%%
from scipy.stats.stats import pearsonr
# todo check why guardian is missing avg_align
# df = df[~df['avg_align'].isna()]
slant = df_sentiment['avg_align']
neg_sentiment = df_sentiment['compound_sentiment']
corr, pval = pearsonr(slant, neg_sentiment)

#%%
from statsmodels import corrcoef

corrcoef(slant, neg_sentiment)
#%%
df_sentiment.to_csv("test_aggr.csv")
#%%
#########################################################
# analysis of GNEWS sentiments
#########################################################
import pandas as pd
import numpy as np

# load newspaper articles
df_dec = pd.read_csv("chatgpt/chatgpt_news_dec.csv")
df_dec = df_dec.drop_duplicates('url')
df_dec = df_dec.iloc[::-1]
print(df_dec.shape)
df_jan = pd.read_csv("chatgpt/chatgpt_news_jan.csv")
df_jan = df_jan.drop_duplicates('url')
df_jan = df_jan.iloc[::-1]
print(df_jan.shape)

df_feb = pd.read_csv("chatgpt/chatgpt_news_feb.csv")
df_feb = df_feb.drop_duplicates('url')
df_feb = df_feb.iloc[::-1]
print(df_feb.shape)

df_slant = pd.read_csv("chatgpt/top500.csv")
#%%
df = df_dec.append(df_jan)
df = df.append(df_feb)
df = df.reset_index(drop=True)
df_normalized = pd.json_normalize(df["source"].apply(eval))
df_normalized = df_normalized.rename(columns={"url": 'domain'})
df = pd.concat([df, df_normalized], axis=1)

#%%
replaced_items = ["www.", "markets.", ".com"]
df['domain'] = df['domain'].replace("https://", '', regex=True)
df["dom"] = df["domain"]
for item in replaced_items:
    df['dom'] = df['dom'].replace(item, '', regex=True)

def check_all_strings(row, b_df):
    a_strings = row['dom'].split()
    b_strings = b_df['domain'].tolist()
    matching_strings = [b for a in a_strings for b in b_strings if a in b]
    return matching_strings

df["included"] = df.apply(check_all_strings, axis=1, args=(df_slant,))

# df["no_domains"] = df["included"].apply(lambda x: len(x))
#%%
def remove_items(row):
    if len(row['included']) > 1:
        domain = row['domain']
        row['included'] = [item for item in row['included'] if item == domain]
    if len(row['included']) == 1:
        row['included'] = row['included'][0]
    else:
        row['included'] = ''
    return row
print(df["included"].value_counts())
df = df.apply(remove_items, axis=1)
#%%
# df.loc[df["included"].apply(len)== 0, 'included']== pd.NaT
df = pd.merge(df, df_slant, how="left", left_on="included", right_on="domain")
#%%
#########################################
# Number of newspaper articles per slant
#########################################

import matplotlib.pyplot as plt

fig, ax = plt.subplots()

ax.hist(df["avg_align"], bins=20, range=(-1, 1), edgecolor='black')
ax.set_xlabel('slant')
ax.set_xlim([-1,1])

ax.set_ylabel('count')
fig.savefig('chatgpt/news-slant.png')
plt.show()
#%%
#########################################
# todo Calculate Sentiments for title
#########################################
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()
df["vader_sentiment"] = df["title"].apply(lambda x: analyzer.polarity_scores(x))

df['neg_sentiment'] = df['vader_sentiment'].apply(lambda x: x['neg']).groupby(df['dom']).transform('mean')
df['neu_sentiment'] = df['vader_sentiment'].apply(lambda x: x['neu']).groupby(df['dom']).transform('mean')
df['pos_sentiment'] = df['vader_sentiment'].apply(lambda x: x['pos']).groupby(df['dom']).transform('mean')
df['comp_sentiment'] = df['vader_sentiment'].apply(lambda x: x['compound']).groupby(df['dom']).transform('mean')

df_sentiment = df.groupby("avg_align", as_index=False).first()
#%%
fig, ax = plt.subplots()

x = df_sentiment["avg_align"]
y = df_sentiment["comp_sentiment"]
ax.scatter(x,y)
plt.axhline(y=0, color='k', linestyle='-')
ax.set_xlabel("slant")
ax.set_ylabel("compound sentiment")

# fit linear regression with Least squares
b,a = np.polyfit(x, y, deg=1)

ax.plot(x,a + b*x)

plt.show()
#%%
# calculate average sentiment for liberal vs. conservative slant

# create conditions for avg_align
cond1 = df['avg_align'] > 0
cond3 = df['avg_align'] < 0

# calculate mean of neg, neu, pos, compound for each condition
neg_mean_cond1 = df.loc[cond1, 'neg_sentiment'].mean()
neu_mean_cond1 = df.loc[cond1, 'neu_sentiment'].mean()
pos_mean_cond1 = df.loc[cond1, 'pos_sentiment'].mean()
compound_mean_cond1 = df.loc[cond1, 'comp_sentiment'].mean()
print(compound_mean_cond1)
neg_mean_cond3 = df.loc[cond3, 'neg_sentiment'].mean()
neu_mean_cond3 = df.loc[cond3, 'neu_sentiment'].mean()
pos_mean_cond3 = df.loc[cond3, 'pos_sentiment'].mean()
compound_mean_cond3 = df.loc[cond3, 'comp_sentiment'].mean()
print(compound_mean_cond3)

#%%
#########################################
# todo Calculate Vader Sentiments (lexicographic)
#########################################
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

sentiment_var = "title"
analyzer = SentimentIntensityAnalyzer()
df["vader_sentiment"] = df[sentiment_var].apply(lambda x: analyzer.polarity_scores(x))

df['neg_sentiment'] = df['vader_sentiment'].apply(lambda x: x['neg']).groupby(df['dom']).transform('mean')
df['neu_sentiment'] = df['vader_sentiment'].apply(lambda x: x['neu']).groupby(df['dom']).transform('mean')
df['pos_sentiment'] = df['vader_sentiment'].apply(lambda x: x['pos']).groupby(df['dom']).transform('mean')
df['comp_sentiment'] = df['vader_sentiment'].apply(lambda x: x['compound']).groupby(df['dom']).transform('mean')

df_sentiment = df.groupby("avg_align", as_index=False).first()
#%%
fig, ax = plt.subplots()

x = df_sentiment["avg_align"]
y = df_sentiment["comp_sentiment"]
ax.scatter(x,y)
plt.axhline(y=0, color='k', linestyle='-')
ax.set_xlabel("slant")
ax.set_ylabel("compound sentiment")

# fit linear regression with Least squares
b,a = np.polyfit(x, y, deg=1)

ax.plot(x,a + b*x)

plt.show()
#%%
# calculate average sentiment for liberal vs. conservative slant

# create conditions for avg_align
cond1 = df['avg_align'] > 0
cond3 = df['avg_align'] < 0

# calculate mean of neg, neu, pos, compound for each condition
neg_mean_cond1 = df.loc[cond1, 'neg_sentiment'].mean()
neu_mean_cond1 = df.loc[cond1, 'neu_sentiment'].mean()
pos_mean_cond1 = df.loc[cond1, 'pos_sentiment'].mean()
compound_mean_cond1 = df.loc[cond1, 'comp_sentiment'].mean()
print(compound_mean_cond1)
neg_mean_cond3 = df.loc[cond3, 'neg_sentiment'].mean()
neu_mean_cond3 = df.loc[cond3, 'neu_sentiment'].mean()
pos_mean_cond3 = df.loc[cond3, 'pos_sentiment'].mean()
compound_mean_cond3 = df.loc[cond3, 'comp_sentiment'].mean()
print(compound_mean_cond3)

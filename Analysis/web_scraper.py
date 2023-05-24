#%%
# # Gnews.io API scraper
# import json
# import urllib.request
# import pandas as pd
# import time
#
# apikey = "c2918649c0c63106c030c9b55e9f0efd"
# # url = f"https://gnews.io/api/v4/search?q=christmas&lang=en&country=us&from=2022-11-30T00:00:00Z&to=2023-01-01T00:00:00Z&sortby=publishedAt&apikey={apikey}"
# # url = f"https://gnews.io/api/v4/search?q=" + urllib.parse.quote("chatgpt foxnews") + f"&lang=en&country=us&from={start_date}&to={end_date}&sortby=publishedAt&apikey={apikey}"
# #2023-02-09T05:00:00Z
# #2023-02-08T05:00:00Z
#
# # "2022-11-30T00:00:00Z"
# start_date = "2022-11-30T00:00:00Z"
# end_date = "2023-03-07T00:00:00Z"
# df_news = pd.DataFrame()
# # df = df.drop_duplicates('url')
#
# #%%
# import urllib.parse
# i = 0
# while i < 1:
#     # search query     url = f"https://gnews.io/api/v4/search?q=chatgpt&lang=en&country=us&from={start_date}&to={end_date}&sortby=publishedAt&apikey={apikey}"
#     url = f"https://gnews.io/api/v4/search?q=chatgpt&lang=en&country=us&from={start_date}&to={end_date}&sortby=publishedAt&apikey={apikey}"
#     with urllib.request.urlopen(url) as response:
#         # if response.status_code == 429:
#         #     time.sleep(int(response.headers["Retry-After"]))
#         data = json.loads(response.read().decode("utf-8"))
#         articles = data["articles"]
#     print(i)
#     print("last article:", f"{articles[-1]['publishedAt']}")
#     print("end date:", end_date)
#     if end_date == f"{articles[-1]['publishedAt']}":
#         end_date = end_date[:11]+"04:59:59Z"
#     else:
#         end_date = f"{articles[-1]['publishedAt']}"
#     df_news = df_news.append(articles)
#
#     if len(articles) < 10:
#         break
#     i += 1
#     time.sleep(3)
#
# df_news.to_csv("chatgpt_news_foxnews.csv", index=False, encoding="utf-8-sig")
# # df = df.drop_duplicates('url')
#
# #%%
# import urllib.request
#
# fp = urllib.request.urlopen("https://12ft.io/proxy?&q=https%3A%2F%2Fwww.washingtontimes.com/news/2023/feb/13/chatgpt-struggles-when-asked-to-write-bills-from-c/")
# time.sleep(2)
# mybytes = fp.read()
#
# mystr = mybytes.decode("utf8")
# fp.close()
#
# print(mystr)

#%%
import requests
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
import re
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import random
import json
import os

HEADER = [
    ({"User-Agent": "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)"}),
    ({"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko"}),
    ({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763"}),
    ({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}),
    ({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36"}),
    ({"User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko"}),
    ({"User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; .NET CLR 1.1.4322)"}),
    ({"User-Agent": "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)"}),
    ({"User-Agent": "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)"}),
    ({"User-Agent": "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; .NET CLR 1.1.4322)"})
]
print(os.getcwd())
df_slant = pd.read_csv("top500.csv")

# List of URLs to scrape
df_slant["domain"] = df_slant["domain"].str.lstrip("m.")
df_slant["website"] = "https://" + df_slant["domain"]
urls = df_slant["website"]#[174:177]

# List to store the scraped data
results, twitter_links = [], []
i = 2

# Loop through each URL in the list
for url in urls:
    print(i, url)
    i += 1

    try:
        # Make an HTTP request to the URL
        response = requests.get(url, headers=random.choice(HEADER))
        # response.raise_for_status()
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as err:
        print(f"Error: {err}")
        results.append(['down'])
        continue

    # Parse the HTML response with BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")

    # Define regular expressions to match different types of links
    # regex = re.compile(r".*twitter\.com\/.*")
    href_regex = re.compile(r".*twitter\.com\/.*")
    # sameas_regex = re.compile(
    #     r".*schema\.org\/(Twitter|SocialMediaPosting)\".*sameAs\".*twitter\.com\/[^\/\\]*(?:\\.[^\/\\]*)*")
    # metatag_regex = re.compile(r".*twitter:\w+\".*twitter\.com\/[^\/\\]*(?:\\.[^\/\\]*)*")

    # Find all links containing Twitter URL
    twitter_links = [link['href'] for link in soup.find_all('a') if href_regex.match(link.get('href', ''))]

    if twitter_links == []:
        twitter_site_element = soup.find('meta', attrs={'name': 'twitter:site'})
        # twitter_site_element = soup.find('meta', attrs={'name': re.compile('^twitter:.*')})
        if twitter_site_element is None:
            twitter_site_element = soup.find('meta', attrs={'name': 'twitter:title'})

        if twitter_site_element is not None:
            try:
                handle = twitter_site_element['content']
            except KeyError as err:
                print(f"Error: {err}")
                try:
                    handle = twitter_site_element['value']
                except KeyError as err:
                    print(f"Error: {err}")

            if handle[0] == "@":
                metatag_links = ['https://twitter.com/' + handle[1:]]
            else:
                metatag_links = ['https://twitter.com/' + handle]

            # Combine all the links found
            twitter_links += metatag_links

        # find twitter from nationalreview aka nro
        # if twitter_links == []:
        #     print(2)
        #     script_tags = soup.find_all('script')
        #     # loop through all script tags to find the one containing 'site_social_links'
        #     for script_tag in script_tags:
        #         if ("site_social_links" in script_tag.contents):
        #             print('found')
        #             # extract the JSON string from the script tag
        #             json_str = script_tag.text.strip().split(' = ')[1].rstrip(';')
        #             # parse the JSON string into a Python object
        #             social_links = json.loads(json_str)
        #             # get the twitter link
        #             twitter_link = social_links['site_social_links']['twitter']
        #             # print the twitter link
        #             print(twitter_link)

    # Add the results to the list
    results.append(list(set(twitter_links)))


# Convert the results list to a pandas DataFrame with one column
df_slant["Twitter"] = results

df_slant.to_csv("top500twitter.csv", index=False)
#%%
#########################################################
# extract twitter handles from list of twitter links
#########################################################
import pandas as pd
import ast
import re

df_slant = pd.read_csv("top500twitter.csv")

df_slant["twitt_list"] = df_slant["Twitter"]
df_slant["twitt_list"] = df_slant["twitt_list"].apply(ast.literal_eval)
df_slant["twitt_list"] = df_slant["twitt_list"].apply(lambda x: list(set(map(str.lower, x))))

#%%
df_slant["twitt_list"] = df_slant["twitt_list"].apply(lambda x: [s.split('?ref')[0] if '?ref' in s else s for s in x])
df_slant["twitt_list"] = df_slant["twitt_list"].apply(lambda x: [s[:-1] if s.endswith('/') else s for s in x])
df_slant["twitt_list"] = df_slant["twitt_list"].apply(lambda x: [s.replace('http://', 'https://') if s.startswith('http://') else s for s in x])
df_slant["twitt_list"] = df_slant["twitt_list"].apply(lambda x: ["https://twitter.com/" + re.search(r'screen_name=([^&]+)', s).group(1) if '/intent/follow' in s else s for s in x])

#%%
# convert to lowercase then only keep unique twitter links
df_slant["twitt_list"] = df_slant["twitt_list"].apply(lambda x: list(set(map(str.lower, x))))
df_slant['twitt_list'] = df_slant['twitt_list'].apply(lambda x: [s.replace('bideutschland', 'businessinsider') for s in x])
df_slant["twitt_list"] = df_slant["twitt_list"].apply(lambda x: [s.replace('https://twitter.com/vice_de', 'https://twitter.com/vice') for s in x])
df_slant["twitt_list"] = df_slant["twitt_list"].apply(lambda x: [s.split('?lang')[0] if '?lang' in s else s for s in x])

# remove twitter links without handle (twitter.com/), with /intent/tweet and replace /intent/follow/ with actual handle
# cut off at "?ref"

# Define a list of lambda functions that remove unwanted strings
conditions = [
    lambda s: "down" not in s,
    lambda s: "kdaj" not in s,
    lambda s: "status" not in s,
    lambda s: "/intent/tweet" not in s,
    lambda s: "share?" not in s,
    lambda s: "i/events" not in s,
    lambda s: not s.endswith("twitter.com"),
    lambda s: not s.endswith("twitter.com/#")
]

# Define a function that removes strings based on the conditions
def remove_strings(df, column, conditions):
    remove_strings_func = lambda lst: [s for s in lst if all(cond(s) for cond in conditions)]
    df[column] = df[column].apply(remove_strings_func)
    return df

# Apply the function to the 'Twitter' column
df_slant = remove_strings(df_slant, 'twitt_list', conditions)
#%%
df_slant["handles"] = [[s.split('/')[-1] for s in lst] for lst in df_slant["twitt_list"]]
df_slant["handles"] = df_slant["handles"].apply(lambda x: list(set(map(str.lower, x))))

#%%
df_slant.to_csv("top500twitterhandles.csv")

# todo remove all other twitter_acc for commonnews and share from libertynews, twitters own handles, foreign languages
# todo in the end of code try twitter.com/"website_name" for bloomberg etc.
# todo nro, dailymailUK/dailymail, ibdinvestors (news.investors) still missing
import pandas as pd
from scipy.stats.stats import pearsonr
df = pd.read_csv("survey.csv")
df = df[pd.notnull(df["submitdate"])]

dict_cells = {
    "Yes": 1,
    "No": 0,
    "Male": 1,
    "Female": 0,
    "Democrat": -1,
    "Independent": 0,
    "Republican": 1,
}

dict_col = {
    "d1": "age",
    "D3": "sex",
    "d2": "degree",
    "d5": "job",
    "d4[SQ002]": "risk_aver",
    "d4[SQ004]": "best_intention",
    "d4[SQ006]": "reciproc1",
    "d4[SQ007]": "reciproc2_neg",
    "d6[SQ005]": "fox",
    "d6[SQ006]": "wsj",
    "d6[SQ007]": "wp",
    "d6[SQ008]": "cnn",
    "d6[SQ009]": "abc",
    "d6[SQ010]": "reuters",
    "d6[SQ011]": "econ",
    "d6[SQ012]": "nyt",
    "d6[SQ013]": "time",
    "d6[SQ014]": "forbes",
    "d6[SQ015]": "none",
    "d8[SQ57672]": "pol_views",
    "d9[SQ004]":"ladder_me",
    "d9[SQ001]":"ladder_repub",
    "d9[SQ003]":"ladder_demo",
    "d9[SQ002]":"ladder_indep",
    "d11": "pol_party",
    "po2[SQ57672]": "chatgpt_pol",
    "po3[SQ57672]": "bert_pol",
    "po4[SQ57672]": "llama_pol",
    "a1": "chatgpt_know",
    "a2": "chatgpt_use",
    "a7[SQ001]": "chatgpt_perc_acc",
    "a5": "llama_know",
    "a6": "llama_use",
    "a9[SQ001]": "llama_perc_acc",
    "a3": "bert_know",
    "a4": "bert_use",
    "a8[SQ001]": "bert_perc_acc",
    "po5[SQ57672]": "openai_pol",
    "po6[SQ57672]": "meta_pol",
    "po7[SQ57672]": "twitter_pol",
    "po8[SQ57672]": "apple_pol",
    "po9[SQ57672]": "exxon_pol",
    "at1[SQ57672]": "chatgpt_att1",
    "at1[SQ003]": "chatgpt_att2",
    "at1[SQ004]": "chatgpt_att3",
    "at1[SQ005]": "chatgpt_att4",
    "at1[SQ006]": "chatgpt_att5",
    "at1[SQ007]": "chatgpt_att6",
    "at2[SQ57672]": "bert_att1",
    "at2[SQ003]": "bert_att2",
    "at2[SQ004]": "bert_att3",
    "at2[SQ005]": "bert_att4",
    "at2[SQ006]": "bert_att5",
    "at2[SQ007]": "bert_att6",
    "at3[SQ57672]": "llama_att1",
    "at3[SQ003]": "llama_att2",
    "at3[SQ004]": "llama_att3",
    "at3[SQ005]": "llama_att4",
    "at3[SQ006]": "llama_att5",
    "at3[SQ007]": "llama_att6",
}

df = df.replace(dict_cells)
df = df.rename(columns=dict_col)
df["reciproc2"] = 11 - df["reciproc2_neg"]
df["reciproc"] = (df["reciproc1"] + df["reciproc2"]) / 2

df["chatgpt_att_avg"] = (df["chatgpt_att1"] + df["chatgpt_att2"] +
                              df["chatgpt_att3"] + df["chatgpt_att4"] +
                              df["chatgpt_att5"] + df["chatgpt_att6"]) / 6

df["llama_att_avg"] = (df["llama_att1"] + df["llama_att2"] +
                              df["llama_att3"] + df["llama_att4"] +
                              df["llama_att5"] + df["llama_att6"]) / 6

df["chatgpt_pol_dis"] = abs(df["chatgpt_pol"] - df["pol_views"])
df["openai_pol_dis"] = abs(df["openai_pol"] - df["pol_views"])

df["bert_pol_dis"] = abs(df["bert_pol"] - df["pol_views"])
# df["google_pol_dis"] = abs(df["openai_pol"] - df["pol_views"])

df["llama_pol_dis"] = abs(df["llama_pol"] - df["pol_views"])
df["meta_pol_dis"] = abs(df["meta_pol"] - df["pol_views"])

df["chatgpt_perc_acc"] = df["chatgpt_perc_acc"] / 5
df["llama_perc_acc"] = df["llama_perc_acc"] / 5
df["bert_perc_acc"] = df["bert_perc_acc"] / 5


# define method for normalization
def normalize_col(my_series):
    normalized_series = (my_series - my_series.min()) / \
                        (my_series.max() - my_series.min())
    return normalized_series

# df["chatgpt_att_avg"] = normalize_col(df["chatgpt_att_avg"])
# df["llama_att_avg"] = normalize_col(df["llama_att_avg"])
#
# df["chatgpt_pol_dis"] = normalize_col(df["chatgpt_pol_dis"])
# df["openai_pol_dis"] = normalize_col(df["openai_pol_dis"])
# df["llama_pol_dis"] = normalize_col(df["llama_pol_dis"])
# df["meta_pol_dis"] = normalize_col(df["meta_pol_dis"])
#
# df["chatgpt_pol"] = normalize_col(df["chatgpt_pol"])
# df["openai_pol"] = normalize_col(df["openai_pol"])
# df["llama_pol"] = normalize_col(df["llama_pol"])
# df["meta_pol"] = normalize_col(df["meta_pol"])
#
# df["pol_views"] = normalize_col(df["pol_views"])

df["job_int"] = pd.factorize(df["job"])[0]
df["deg_int"] = pd.factorize(df["degree"])[0]

df.to_csv("survey_data.csv")

cor = df.corr()

#%%
df_know = df[df["bert_know"] == 1]
cor = df_know.corr()

corr, pval = pearsonr(df_know["pol_views"], df_know["chatgpt_att_avg"])

print(corr)
print(pval)

#%%
#######################
# ChatGPT pol dis
#######################
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy import stats

df_x = df_know.groupby("chatgpt_pol_dis").mean()
fig, ax = plt.subplots(figsize=(8,6))

x = df_x.index
y = df_x["chatgpt_att_avg"]
std = df_know.groupby("chatgpt_pol_dis").std()

n=df_know.shape[0]
# y_err = std / np.sqrt(n) * stats.t.ppf(1-0.05/2, n-1)

ax.bar(x,y, alpha = 0.5)

ax.set_xlabel("Difference between people's pol. orientation and ChatGPT's perceived pol. orientation")
ax.set_ylabel("People's positive perception of ChatGPT")
# x = df_x["chatgpt_pol_dis"]
# y = df_x["chatgpt_att2"]

plt.tight_layout()
fig.savefig('chatgpt_pol_dis_attitute.png')
# ax.legend()
plt.show()

# bins = pd.cut(x, bins=3)
#
#
# # Group the data by the bins and calculate the mean y-value for each bin
# grouped_data = df_x.groupby(bins)['chatgpt_att_avg'].mean()
#
# # Plot the bar plot
# grouped_data.plot(kind='bar')

# # fit linear regression with Least squares
# b,a = np.polyfit(x, y, deg=1)
#
# ax.plot(x,a + b*x)#, color='k')

#%%
#######################
# binned difference between openAI pol dis and attitude towards chatgpt
#######################

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats.stats import pearsonr

df = pd.read_csv("survey_data.csv")

fig, ax = plt.subplots(figsize=(8,6))

# Generate some example data
x = df["openai_pol_dis"]
y = df["chatgpt_att_avg"]

# Define custom bin edges and labels
bin_edges = [-0.5,1.5,3.5,6.5]
# bin_edges = [-0.5,0.2,0.51,1.1]
bin_labels = ['low', 'medium', 'high']

# Bin the x-values
# bins = pd.cut(x, bins=[edge[0] for edge in bin_edges] + [bin_edges[-1][1]], labels=bin_labels)
# Bin the x-values
x_binned = pd.cut(x, bins=bin_edges, labels=bin_labels)

# Calculate the mean of the y-values for each bin
df_x = pd.DataFrame({'x': x, 'y': y})
df_x['x_binned'] = x_binned
y_means = df_x.groupby('x_binned')['y'].mean().values

# Plot the binned x-values and mean y-values
ax.bar(bin_labels, y_means, alpha=0.5)

# Set axis labels
ax.set_xlabel("Distance between individuals' pol. orientation and OpenAI's perceived pol. orientation")
ax.set_ylabel("Individuals' average positive perception of ChatGPT")
plt.tight_layout()
# Show the plot
fig.savefig('openai_pol_dis_attitute.png')

plt.show()

corr, pval = pearsonr(df["openai_pol_dis"], df["chatgpt_att_avg"])

print(corr)
print(pval)
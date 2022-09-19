import pandas as pd
import numpy as np

data = pd.read_csv("Data/all_apps_wide-2022-09-06.csv", sep=',')
data = data[data["participant._current_page_name"] == "End"]
print("number of participants: ", data.shape[0])
data.columns = data.columns.str.removeprefix("si_experiment.1.player.")
data.columns = data.columns.str.removeprefix("participant.")

#%%
df = data.iloc[:,13:len(data.columns)-2]
df.drop(list(df.filter(regex = 'session')), axis = 1, inplace = True)

#%%
# todo: extract advice (pred) of ai to use as variable to calc WOA for both tasks

def format_german_number(number, precision=0):
    # build format string
    format_str = '{{:,.{}f}}'.format(precision)

    # make number string
    number_str = format_str.format(number)

    # replace chars
    return number_str.replace(',', 'X').replace('.', ',').replace('X', '.')


apartments = pd.read_csv("Frontend/Data/immonet_data_selected.csv")
apartments = apartments[['pred_price']]


#%%

# create dummy treatment var dev, acc for analyses
df["treat_dev"] = np.where((df["treatment"] == "dev") | (df["treatment"] == "both"), 1, 0)
df["treat_acc"] = np.where((df["treatment"] == "acc") | (df["treatment"] == "both"), 1, 0)

# create dummy for dev = 1 / 0 while acc constant else not defined
# create dummy for acc = 1 / 0 while dev constant else not defined
df["dev_no_acc"] = np.select(
    [(df["treat_acc"] == 0) & (df["treat_dev"] == 1),
    (df["treat_acc"] == 0) & (df["treat_dev"] == 0)],
    [1,0], default=np.nan)
df["dev_acc"] = np.select(
    [(df["treat_acc"] == 1) & (df["treat_dev"] == 1),
    (df["treat_acc"] == 1) & (df["treat_dev"] == 0)],
    [1,0], default=np.nan)
df["acc_no_dev"] = np.select(
    [(df["treat_acc"] == 1) & (df["treat_dev"] == 0),
    (df["treat_acc"] == 0) & (df["treat_dev"] == 0)],
    [1,0], default=np.nan)
df["acc_dev"] = np.select(
    [(df["treat_acc"] == 1) & (df["treat_dev"] == 1),
    (df["treat_acc"] == 0) & (df["treat_dev"] == 1)],
    [1,0], default=np.nan)

# reverse attention checks measurements = 8 - #
df["integ_trust_t1_2"] = 8 - df["integ_trust_t1_2"]
df["emo_trust_t1_1"] = 8 - df["emo_trust_t1_1"]
df["integ_trust_t2_2"] = 8 - df["integ_trust_t2_2"]
df["emo_trust_t2_1"] = 8 - df["emo_trust_t2_1"]

# avg aggr of constructs
df["pers_inno"] = (df["pers_inno1"] + df["pers_inno2"] + df["pers_inno3"]) / 3
df["comp_trust_t1"] = (df["cog_trust_t1_1"] + df["cog_trust_t1_2"] + df["cog_trust_t1_3"]) / 3
df["comp_trust_t2"] = (df["cog_trust_t2_1"] + df["cog_trust_t2_2"] + df["cog_trust_t2_3"]) / 3
df["integ_trust_t1"] = (df["integ_trust_t1_1"] + df["integ_trust_t1_2"] + df["integ_trust_t1_3"]) / 3
df["integ_trust_t2"] = (df["integ_trust_t2_1"] + df["integ_trust_t2_2"] + df["integ_trust_t2_3"]) / 3
df["emo_trust_t1"] = (df["emo_trust_t1_1"] + df["emo_trust_t1_2"] + df["emo_trust_t1_3"]) / 3
df["emo_trust_t2"] = (df["emo_trust_t2_1"] + df["emo_trust_t2_2"] + df["emo_trust_t2_3"]) / 3
df["soc_dist_t1"] = (df["soc_distance_t1_1"] + df["soc_distance_t1_2"] + df["soc_distance_t1_3"]) / 3
df["soc_dist_t2"] = (df["soc_distance_t2_1"] + df["soc_distance_t2_2"] + df["soc_distance_t2_3"]) / 3
df["anthro_t1"] = (df["anthro_t1_1"] + df["anthro_t1_2"] + df["anthro_t1_3"]) / 3
df["anthro_t2"] = (df["anthro_t2_1"] + df["anthro_t2_2"] + df["anthro_t2_3"]) / 3

# todo convert strings to ints
soc_dist = {
    "Geschlecht": 0,
    "Migrationshintergrund": 1,
    "Politsche Ansichten": 2
}

df.to_csv("Data/data.csv", sep=',')
# df["soc_dist_rank_t1"] = df["soc_dist_rank_t1_1"] + df["soc_dist_rank_t1_2"] + df["soc_dist_rank_t1_3"]
# df["soc_dist_rank_t2"] = (df["soc_dist_rank_t2_1"] + df["soc_dist_rank_t2_2"] + df["soc_dist_rank_t2_3"])
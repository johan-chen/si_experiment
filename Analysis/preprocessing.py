import pandas as pd
import numpy as np
from Analysis.misc_methods import *

# read in data
data = pd.read_csv("Data/all_apps_wide_2022-09-16.csv", sep=',')
data = data[data["participant._current_page_name"] == "End"]
print("number of participants: ", data.shape[0])
data.columns = data.columns.str.replace("si_experiment.1.player.", "", regex=True)
data.columns = data.columns.str.replace("participant.", "", regex=True)

# read in prolific data
prolific_data = pd.read_csv("Data/prolific_export_si1.csv").append(
    pd.read_csv("Data/prolific_export_si2.csv"))

# join prolific data
data = data.join(other=prolific_data.set_index("Participant id", drop=True), on="label")

# read in task instances
immo_data = pd.read_csv("Frontend/Data/immonet_data_selected.csv")
credit_data = pd.read_csv("Frontend/Data/lending_data_selected.csv")

# read in dev data
dev_data = pd.read_csv("Frontend/Data/dev_profiles.csv")

# clean some columns
df = data.iloc[:, 13:len(data.columns)]
df.drop(list(df.filter(regex='session')), axis=1, inplace=True)


# define method for normalization
def normalize_col(my_series):
    normalized_series = (my_series - my_series.min()) / \
                        (my_series.max() - my_series.min())
    return normalized_series


# get AI predictions for WTP and WOA stage
# %% (if tasks_order = 1: credit is always WOA, immo only if WTP > ai_prob; o/w reverse)
ai_pred_woa_stage, ai_pred_wtp_stage, \
woa_stage_step_size, wtp_stage_step_size, \
    = [], [], [], []
for i, p in df.iterrows():
    if p.tasks_order == 0:
        ai_pred_woa_stage.append(
            round((immo_data.iloc[p.apartment_row]["pred_price"] - 300_000) / 40_000) * 40_000 + 300_000)
        woa_stage_step_size.append(40_000)
        ai_pred_wtp_stage.append(credit_data.iloc[p.lender_row]["pred_"])
        wtp_stage_step_size.append(10)
    elif p.tasks_order == 1:
        ai_pred_woa_stage.append(credit_data.iloc[p.lender_row]["pred_"])
        woa_stage_step_size.append(10)
        ai_pred_wtp_stage.append(
            round((immo_data.iloc[p.apartment_row]["pred_price"] - 300_000) / 40_000) * 40_000 + 300_000)
        wtp_stage_step_size.append(40_000)
    else:
        raise Exception(f"Check tasks_order = {p.tasks_order} of index {p.index}.")
df["ai_pred_woa_stage"], df["ai_pred_wtp_stage"] = ai_pred_woa_stage, ai_pred_wtp_stage
df["woa_stage_step_size"], df["wtp_stage_step_size"] = woa_stage_step_size, wtp_stage_step_size

# get WOA guesses normalized
df["guess_1_woa"] = df["task2Estimate"].copy(deep=True)
df.loc[df["guess_1_woa"] > 1000, "guess_1_woa"] = df["guess_1_woa"] - 300_000
df["guess_1_woa"] = normalize_col(df["guess_1_woa"] / df["woa_stage_step_size"])
df["guess_2_woa"] = df["revision2"].copy(deep=True)
df.loc[df["guess_2_woa"] > 1000, "guess_2_woa"] = df["guess_2_woa"] - 300_000
df["guess_2_woa"] = normalize_col(df["guess_2_woa"] / df["woa_stage_step_size"])

# get WOA averages for treatment groups
# WOA = (final estimation - initial estimation) / (advisor’s estimation - initial estimation)
df["woa"] = (df.revision2 - df.task2Estimate) / (df.ai_pred_woa_stage - df.task2Estimate)
df["woa"].replace([np.inf, -np.inf], np.nan, inplace=True)
df["stage_woa_rel_adj"] = abs(df.revision2 - df.task2Estimate) / df.woa_stage_step_size
df["stage_woa_rel_adj"].replace([np.inf, -np.inf], np.nan, inplace=True)

# get WOA and WTP developer characteristics
social_char_dict = {
    "eher links": 2, "mitte": 5, "eher rechts": 8,
    "ja": 1, "nein": 0,
    "divers": 0, "weiblich": 1, "männlich": 2}
wtp_dev, woa_dev = [dev_data.iloc[i] for i in df["dev_row1"]], [dev_data.iloc[i] for i in df["dev_row2"]]
df["wtp_dev_sex"] = [social_char_dict[wtp_dev[i]["gender"]] for i in range(0, len(wtp_dev))]
df["wtp_dev_migration"] = [social_char_dict[wtp_dev[i]["migrant"]] for i in range(0, len(wtp_dev))]
df["wtp_dev_pol"] = [social_char_dict[wtp_dev[i]["politics"]] for i in range(0, len(wtp_dev))]
df["woa_dev_sex"] = [social_char_dict[woa_dev[i]["gender"]] for i in range(0, len(woa_dev))]
df["woa_dev_migration"] = [social_char_dict[woa_dev[i]["migrant"]] for i in range(0, len(woa_dev))]
df["woa_dev_pol"] = [social_char_dict[woa_dev[i]["politics"]] for i in range(0, len(woa_dev))]

# social distance to dev
# ...wtp
df["sex_dis_wtp"] = (df["wtp_dev_sex"] != df["sex"]).astype(int)
df["mig_dis_wtp"] = (df["wtp_dev_migration"] != df["migration_bg"]).astype(int)
pol_dis_wtp_abs = abs(df["wtp_dev_pol"] - df["pol_views"])
df["pol_dis_wtp"] = normalize_col(pol_dis_wtp_abs)

df["sexmig_dis_wtp"] = normalize_col(df["sex_dis_wtp"] + df["mig_dis_wtp"])
df["sexpol_dis_wtp"] = normalize_col(df["sex_dis_wtp"] + df["pol_dis_wtp"])
df["migpol_dis_wtp"] = normalize_col(df["mig_dis_wtp"] + df["pol_dis_wtp"])

df["soc_dis_wtp"] = df["sex_dis_wtp"] + df["mig_dis_wtp"] + df["pol_dis_wtp"]
df["soc_dis_wtp"] = normalize_col(df["soc_dis_wtp"])
df["soc_dis_wtp_w"] = df["sex_dis_wtp"] * df["importance_sex"] + \
                       df["mig_dis_wtp"] * df["importance_migration_bg"] + \
                       df["pol_dis_wtp"] * df["importance_pol_views"]
df["soc_dis_wtp_w"] = normalize_col(df["soc_dis_wtp_w"])

# ...woa
df["sex_dis_woa"] = (df["woa_dev_sex"] != df["sex"]).astype(int)
df["mig_dis_woa"] = (df["woa_dev_migration"] != df["migration_bg"]).astype(int)
pol_dis_woa_abs = abs(df["woa_dev_pol"] - df["pol_views"])
df["pol_dis_woa"] = normalize_col(pol_dis_woa_abs)

df["sexmig_dis_woa"] = normalize_col(df["sex_dis_woa"] + df["mig_dis_woa"])
df["sexpol_dis_woa"] = normalize_col(df["sex_dis_woa"] + df["pol_dis_woa"])
df["migpol_dis_woa"] = normalize_col(df["mig_dis_woa"] + df["pol_dis_woa"])

df["soc_dis_woa"] = df["sex_dis_woa"] + df["mig_dis_woa"] + df["pol_dis_woa"]
df["soc_dis_woa"] = normalize_col(df["soc_dis_woa"])
df["soc_dis_woa_w"] = df["sex_dis_woa"] * df["importance_sex"] + \
                       df["mig_dis_woa"] * df["importance_migration_bg"] + \
                       df["pol_dis_woa"] * df["importance_pol_views"]
df["soc_dis_woa_w"] = normalize_col(df["soc_dis_woa_w"])

# social distance ranks
df["soc_dis_wtp_rank_t1"] = 15 - (df["soc_distance_t1_1"] + df["soc_distance_t1_2"] + df["soc_distance_t1_3"])
df["soc_dis_woa_rank_t2"] = 15 - (df["soc_distance_t2_1"] + df["soc_distance_t2_2"] + df["soc_distance_t2_3"])
df["soc_dis_wtp_rank_t1"] = normalize_col(df["soc_dis_wtp_rank_t1"])
df["soc_dis_woa_rank_t2"] = normalize_col(df["soc_dis_woa_rank_t2"])

# student, age, and gender binaries
df["age"] = normalize_col(df["age"])
df["sex"] = np.where((df["sex"] == 2), 1, 0)
df["student"] = np.where(df["Student status"] == "Yes", 1, 0)

# ________________________________________________________________________________________________

# create dummy treatment var dev, acc for analyses
df["treat_dev"] = np.where((df["treatment"] == "dev") | (df["treatment"] == "both"), 1, 0)
df["treat_acc"] = np.where((df["treatment"] == "acc") | (df["treatment"] == "both"), 1, 0)

# create dummy for dev = 1 / 0 while acc constant else not defined
# create dummy for acc = 1 / 0 while dev constant else not defined
df["dev_no_acc"] = np.select(
    [(df["treat_acc"] == 0) & (df["treat_dev"] == 1),
     (df["treat_acc"] == 0) & (df["treat_dev"] == 0)],
    [1, 0], default=np.nan)
df["dev_acc"] = np.select(
    [(df["treat_acc"] == 1) & (df["treat_dev"] == 1),
     (df["treat_acc"] == 1) & (df["treat_dev"] == 0)],
    [1, 0], default=np.nan)
df["acc_no_dev"] = np.select(
    [(df["treat_acc"] == 1) & (df["treat_dev"] == 0),
     (df["treat_acc"] == 0) & (df["treat_dev"] == 0)],
    [1, 0], default=np.nan)
df["acc_dev"] = np.select(
    [(df["treat_acc"] == 1) & (df["treat_dev"] == 1),
     (df["treat_acc"] == 0) & (df["treat_dev"] == 1)],
    [1, 0], default=np.nan)

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
# df["soc_dist_t1"] = (df["soc_distance_t1_1"] + df["soc_distance_t1_2"] + df["soc_distance_t1_3"]) / 3
# df["soc_dist_t2"] = (df["soc_distance_t2_1"] + df["soc_distance_t2_2"] + df["soc_distance_t2_3"]) / 3
df["anthro_t1"] = (df["anthro_t1_1"] + df["anthro_t1_2"] + df["anthro_t1_3"]) / 3
df["anthro_t2"] = (df["anthro_t2_1"] + df["anthro_t2_2"] + df["anthro_t2_3"]) / 3

# todo convert strings to ints
soc_dist = {
    "Geschlecht": 0,
    "Migrationshintergrund": 1,
    "Politische Ansichten": 2
}

df.to_csv("Data/data.csv", sep=',')
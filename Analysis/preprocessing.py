import pandas as pd
import numpy as np
from Analysis.misc_methods import *

# read in data
data = pd.read_csv("Data/all_apps_wide_2022-09-16.csv", sep=',')
data = data[data["participant._current_page_name"] == "End"]
print("number of participants: ", data.shape[0])
data.columns = data.columns.str.replace("si_experiment.1.player.", "", regex=True)
data.columns = data.columns.str.replace("participant.", "", regex=True)

# read in immo and real estate data to compute ground truth
immo_data = pd.read_csv("Frontend/Data/immonet_data_selected.csv")
credit_data = pd.read_csv("Frontend/Data/lending_data_selected.csv")

# read in prolific data
prolific_data = pd.read_csv("Data/prolific_export_si1.csv").append(
    pd.read_csv("Data/prolific_export_si2.csv"))

# join prolific data
data = data.join(other=prolific_data.set_index("Participant id", drop=True), on="label")

# # preprocessing ______________________________
# ______________________________________________
#
# data = data[data.sex != 0]  # drop non-binarys
#
sex_dic = {"Male": 2, "Female": 1}
data = data.replace({"Sex": sex_dic})
data["sex"] = data["Sex"]
data = data[~data.sex.isna()]
#
data.loc[data['Country of birth'] != "Germany", "migration_bg"] = 1
#
# data.loc[data['Country of birth'] == "Germany", "migration_bg"] = 0
#
# data = data[data.wtp >= 50].copy(deep=True)
#
# _____________________________________________

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

# define method for standardization
def stand_col(my_series):
    stand_series = (my_series - my_series.mean()) / my_series.std()
    return stand_series

# get AI predictions for WTP and WOA stage
# %% (if tasks_order = 1: credit is always WOA, immo only if WTP > ai_prob; o/w reverse)
ai_pred_woa_stage, ai_pred_wtp_stage, \
woa_stage_step_size, wtp_stage_step_size, \
woa_task_case, wtp_task_case, \
woa_y_true, wtp_y_true \
    = [], [], [], [], [], [], [], []
for i, p in df.iterrows():
    if p.tasks_order == 0:
        ai_pred_woa_stage.append(
            round((immo_data.iloc[p.apartment_row]["pred_price"] - 300_000) / 40_000) * 40_000 + 300_000)
        woa_stage_step_size.append(40_000)
        woa_task_case.append(p.apartment_row)
        woa_y_true.append(
            (round((immo_data.iloc[p.apartment_row]["price"] - 300_000) / 40_000) / 10)
        )

        ai_pred_wtp_stage.append(credit_data.iloc[p.lender_row]["pred_"])
        wtp_stage_step_size.append(10)
        wtp_task_case.append(p.lender_row + 10)
        wtp_y_true.append(credit_data.iloc[p.lender_row]["y_"] / (10*10))
    elif p.tasks_order == 1:
        ai_pred_woa_stage.append(credit_data.iloc[p.lender_row]["pred_"])
        woa_stage_step_size.append(10)
        woa_task_case.append(p.lender_row + 10)
        woa_y_true.append(credit_data.iloc[p.lender_row]["y_"] / (10*10))

        ai_pred_wtp_stage.append(
            round((immo_data.iloc[p.apartment_row]["pred_price"] - 300_000) / 40_000) * 40_000 + 300_000
        )
        wtp_stage_step_size.append(40_000)
        wtp_task_case.append(p.apartment_row)
        wtp_y_true.append(round((immo_data.iloc[p.apartment_row]["price"] - 300_000) / 40_000) / 10)
    else:
        raise Exception(f"Check tasks_order = {p.tasks_order} of index {p.index}.")
df["ai_pred_woa_raw"], df["ai_pred_wtp_raw"] = ai_pred_woa_stage, ai_pred_wtp_stage
df["woa_stage_step_size"], df["wtp_stage_step_size"] = woa_stage_step_size, wtp_stage_step_size
df["woa_task_case"], df["wtp_task_case"] = woa_task_case, wtp_task_case
df["woa_y_true"], df["wtp_y_true"] = woa_y_true, wtp_y_true

# get WTP guesses "normalized" (on steps) [addition by MZ 24 May 2023]
df["guess_1_wtp"] = df["task1Estimate"].copy(deep=True)
df.loc[df["wtp_stage_step_size"] == 40_000, "guess_1_wtp"] = df["guess_1_wtp"] - 300_000
df["guess_1_wtp"] = (df["guess_1_wtp"] / df["wtp_stage_step_size"]) / 10
df["guess_2_wtp"] = df["revision"].copy(deep=True)
df.loc[df["wtp_stage_step_size"] == 40_000, "guess_2_wtp"] = df["guess_2_wtp"] - 300_000
df["guess_2_wtp"] = (df["guess_2_wtp"] / df["wtp_stage_step_size"]) / 10

# get WOA guesses "normalized" (on steps)
df["guess_1_woa"] = df["task2Estimate"].copy(deep=True)
df.loc[df["woa_stage_step_size"] == 40_000, "guess_1_woa"] = df["guess_1_woa"] - 300_000
df["guess_1_woa"] = (df["guess_1_woa"] / df["woa_stage_step_size"]) / 10
df["guess_2_woa"] = df["revision2"].copy(deep=True)
df.loc[df["woa_stage_step_size"] == 40_000, "guess_2_woa"] = df["guess_2_woa"] - 300_000
df["guess_2_woa"] = (df["guess_2_woa"] / df["woa_stage_step_size"]) / 10

# get predictions "normalized" (on steps)
df["ai_pred_wtp"] = df["ai_pred_wtp_raw"].copy(deep=True)
df.loc[df["wtp_stage_step_size"] == 40_000, "ai_pred_wtp"] = df["ai_pred_wtp"] - 300_000
df["ai_pred_wtp"] = (df["ai_pred_wtp"] / df["wtp_stage_step_size"]) / 10
df["ai_pred_woa"] = df["ai_pred_woa_raw"].copy(deep=True)
df.loc[df["woa_stage_step_size"] == 40_000, "ai_pred_woa"] = df["ai_pred_woa"] - 300_000
df["ai_pred_woa"] = (df["ai_pred_woa"] / df["woa_stage_step_size"]) / 10

# get WOA averages for treatment groups
# WOA = (final estimation - initial estimation) / (advisor’s estimation - initial estimation)
# WOA_abs = abs(final estimation - initial estimation) / abs(advisor’s estimation - initial estimation)
df["woa"] = (df.revision2 - df.task2Estimate) / (df.ai_pred_woa_raw - df.task2Estimate)
df["woa"].replace([np.inf, -np.inf], np.nan, inplace=True)
df["woa_abs"] = abs(df.revision2 - df.task2Estimate) / abs(df.ai_pred_woa_raw - df.task2Estimate)
df["woa_abs"].replace([np.inf, -np.inf], np.nan, inplace=True)

df["woe"] = abs(df.ai_pred_woa_raw - df.revision2) / abs(df.ai_pred_woa_raw - df.task2Estimate)
df["woe"].replace([np.inf, -np.inf], np.nan, inplace=True)

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
# df["sex_dis_wtp"] = (~(((df["wtp_dev_sex"] == 1) & (df["sex"].isin([0, 1]))) | ((df["wtp_dev_sex"] == 2) & (df["sex"].isin([0, 2]))))).astype(int)
df["sex_dis_wtp"] = (df["wtp_dev_sex"] != df["sex"]).astype(int)
df["mig_dis_wtp"] = (df["wtp_dev_migration"] != df["migration_bg"]).astype(int)

pol_dis_wtp_abs = abs(df["wtp_dev_pol"] - df["pol_views"])
df["pol_dis_wtp"] = normalize_col(pol_dis_wtp_abs)

# standardized
df["sex_dis_wtp_std"] = stand_col(df["sex_dis_wtp"])
df["mig_dis_wtp_std"] = stand_col(df["mig_dis_wtp"])
df["pol_dis_wtp_std"] = stand_col(df["pol_dis_wtp"])

# weighted
df["sex_dis_wtp_w"] = normalize_col(df["sex_dis_wtp"] * df["importance_sex"])
df["mig_dis_wtp_w"] = normalize_col(df["mig_dis_wtp"] * df["importance_migration_bg"])
df["pol_dis_wtp_w"] = normalize_col(df["pol_dis_wtp"] * df["importance_pol_views"])

df["sexmig_dis_wtp"] = normalize_col(df["sex_dis_wtp"] + df["mig_dis_wtp"])
df["sexpol_dis_wtp"] = normalize_col(df["sex_dis_wtp"] + df["pol_dis_wtp"])
df["migpol_dis_wtp"] = normalize_col(df["mig_dis_wtp"] + df["pol_dis_wtp"])

df["soc_dis_wtp"] = df["sex_dis_wtp"] + df["mig_dis_wtp"] + df["pol_dis_wtp"]
df["soc_dis_wtp"] = normalize_col(df["soc_dis_wtp"])
df["soc_dis_wtp_w"] = df["sex_dis_wtp"] * df["importance_sex"] + \
                       df["mig_dis_wtp"] * df["importance_migration_bg"] + \
                       df["pol_dis_wtp"] * df["importance_pol_views"]
df["soc_dis_wtp_w"] = normalize_col(df["soc_dis_wtp_w"])

# standardized weighted
df["sex_dis_wtp_w_std"] = stand_col(df["sex_dis_wtp_w"])
df["mig_dis_wtp_w_std"] = stand_col(df["mig_dis_wtp_w"])
df["pol_dis_wtp_w_std"] = stand_col(df["pol_dis_wtp_w"])

# single weighted relative
df["w_sd_sum"] = df["importance_sex"] + df["importance_migration_bg"] + df["importance_pol_views"]

df["w_sex_wtp"] = df["sex_dis_wtp"] * df["importance_sex"] / df["w_sd_sum"]
df["w_mig_wtp"] = df["mig_dis_wtp"] * df["importance_migration_bg"] / df["w_sd_sum"]
df["w_pol_wtp"] = df["pol_dis_wtp"] * df["importance_pol_views"] / df["w_sd_sum"]

# ...woa
df["sex_dis_woa"] = (df["woa_dev_sex"] != df["sex"]).astype(int)
df["mig_dis_woa"] = (df["woa_dev_migration"] != df["migration_bg"]).astype(int)
pol_dis_woa_abs = abs(df["woa_dev_pol"] - df["pol_views"])
df["pol_dis_woa"] = normalize_col(pol_dis_woa_abs)

# standardized
df["sex_dis_woa_std"] = stand_col(df["sex_dis_woa"])
df["mig_dis_woa_std"] = stand_col(df["mig_dis_woa"])
df["pol_dis_woa_std"] = stand_col(df["pol_dis_woa"])

# weighted
df["sex_dis_woa_w"] = normalize_col(df["sex_dis_woa"] * df["importance_sex"])
df["mig_dis_woa_w"] = normalize_col(df["mig_dis_woa"] * df["importance_migration_bg"])
df["pol_dis_woa_w"] = normalize_col(df["pol_dis_woa"] * df["importance_pol_views"])

df["sexmig_dis_woa"] = normalize_col(df["sex_dis_woa"] + df["mig_dis_woa"])
df["sexpol_dis_woa"] = normalize_col(df["sex_dis_woa"] + df["pol_dis_woa"])
df["migpol_dis_woa"] = normalize_col(df["mig_dis_woa"] + df["pol_dis_woa"])

df["soc_dis_woa"] = df["sex_dis_woa"] + df["mig_dis_woa"] + df["pol_dis_woa"]
df["soc_dis_woa"] = normalize_col(df["soc_dis_woa"])
df["soc_dis_woa_w"] = df["sex_dis_woa"] * df["importance_sex"] + \
                       df["mig_dis_woa"] * df["importance_migration_bg"] + \
                       df["pol_dis_woa"] * df["importance_pol_views"]
df["soc_dis_woa_w"] = normalize_col(df["soc_dis_woa_w"])

# standardized weighted
df["sex_dis_woa_w_std"] = stand_col(df["sex_dis_woa"] * df["importance_sex"])
df["mig_dis_woa_w_std"] = stand_col(df["mig_dis_woa"] * df["importance_migration_bg"])
df["pol_dis_woa_w_std"] = stand_col(df["pol_dis_woa"] * df["importance_pol_views"])

# single weighted relative
df["w_sex_woa"] = df["sex_dis_woa"] * df["importance_sex"] / df["w_sd_sum"]
df["w_mig_woa"] = df["mig_dis_woa"] * df["importance_migration_bg"] / df["w_sd_sum"]
df["w_pol_woa"] = df["pol_dis_woa"] * df["importance_pol_views"] / df["w_sd_sum"]

# social distance ranks
df["soc_dis_wtp_rank_t1"] = 15 - (df["soc_distance_t1_1"] + df["soc_distance_t1_2"] + df["soc_distance_t1_3"])
df["soc_dis_woa_rank_t2"] = 15 - (df["soc_distance_t2_1"] + df["soc_distance_t2_2"] + df["soc_distance_t2_3"])
df["soc_dis_wtp_rank_t1"] = normalize_col(df["soc_dis_wtp_rank_t1"])
df["soc_dis_woa_rank_t2"] = normalize_col(df["soc_dis_woa_rank_t2"])

# social distance custom weighted
importances = ["importance_sex", "importance_migration_bg", "importance_pol_views"]
for i, singular_distance in enumerate(["sex_dis_wtp", "sex_dis_woa", "mig_dis_wtp", "mig_dis_woa",
                                    "pol_median_dis_wtp", "pol_median_dis_woa"]):
    if "pol" in singular_distance:
        df["pol_median_dis_wtp"] = (df.pol_dis_wtp > df.pol_dis_wtp.quantile()).replace({True: 1, False: 0})
        df["pol_median_dis_woa"] = (df.pol_dis_woa > df.pol_dis_woa.quantile()).replace({True: 1, False: 0})
    df.loc[df[singular_distance] == 1, singular_distance + "_w2"] = df[singular_distance] - (5 - df[importances[int(i/2)]])/9
    df.loc[df[singular_distance] == 0, singular_distance + "_w2"] = df[singular_distance] + (5 - df[importances[int(i/2)]])/9
df["soc_dis_wtp_w2"] = normalize_col(df["sex_dis_wtp_w2"] + df["mig_dis_wtp_w2"] + df["pol_median_dis_wtp_w2"])
df["soc_dis_woa_w2"] = normalize_col(df["sex_dis_woa_w2"] + df["mig_dis_woa_w2"] + df["pol_median_dis_woa_w2"])

# student, age, and gender binaries
# create custom migration background
df["age"] = normalize_col(df["age"])
df["sex"] = np.where((df["sex"] == 2), 1, 0)
df["student"] = np.where(df["Student status"] == "Yes", 1, 0)

# get ranking from page with self-reported distances
soc_dist = {
    "Geschlecht": 0,
    "Migrationshintergrund": 1,
    "Politische Ansichten": 2
}

# social distance chosen by self reported rank (use only rank 1)
df = df.replace({"soc_distance_rank_t1_1": soc_dist})
df["soc_dis_ranked_wtp"] = df["pol_dis_wtp"].copy(deep=True)
df.loc[df["soc_distance_rank_t1_1"] == 0, "soc_dis_ranked_wtp"] = df[df["soc_distance_rank_t1_1"] == 0]["sex_dis_wtp"]
df.loc[df["soc_distance_rank_t1_1"] == 1, "soc_dis_ranked_wtp"] = df[df["soc_distance_rank_t1_1"] == 1]["mig_dis_wtp"]


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

# make wtp monetary, normalize and standardize perceived accuracy
df.wtp = df.wtp/100 - 0.5
df.perc_acc = df.perc_acc / 100
df.perc_acc2 = df.perc_acc2 / 100
df["perc_acc_std"] = stand_col(df.perc_acc)
df["perc_acc2_std"] = stand_col(df.perc_acc2)

# create custom accuracy (dev/none --> perc_acc, acc/both --> accuracy that was displayed)
acc_treatments = df.treatment.isin(["acc", "both"])
df["custom_acc_wtp"] = df.perc_acc
df.loc[acc_treatments & (df.tasks_order == 1), "custom_acc_wtp"] = 0.4
df.loc[acc_treatments & (df.tasks_order == 0), "custom_acc_wtp"] = 0.45
df["custom_acc_woa"] = df.perc_acc2
df.loc[acc_treatments & (df.tasks_order == 1), "custom_acc_woa"] = 0.45
df.loc[acc_treatments & (df.tasks_order == 0), "custom_acc_woa"] = 0.4

# expectation gap
df.loc[df.tasks_order == 0, "expectation_gap_acc_wtp"] = df.perc_acc - 0.45
df.loc[df.tasks_order == 1, "expectation_gap_acc_wtp"] = df.perc_acc - 0.4
df.loc[df.tasks_order == 0, "expectation_gap_acc_woa"] = df.perc_acc2 - 0.4
df.loc[df.tasks_order == 1, "expectation_gap_acc_woa"] = df.perc_acc2 - 0.45

################################
#   W R I T E  T O  F I L E    #
################################
# df.to_csv("Data/Versions/data_sex_mig_prolific.csv", sep=',')
df.to_csv("Data/Versions/data_sex_mig_prolific.csv", sep=',')

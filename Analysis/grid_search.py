import pandas as pd
import numpy as np
from scipy.stats import mannwhitneyu
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

# initialize results frame
results_frame = pd.DataFrame()
r_i = 0

data_preserve = data.copy(deep=True)
for foc_sex in ["otree", "otree_nonbinary", "prolific_only", "prolific_otree_same"]:
    data = data_preserve.copy(deep=True)

    if foc_sex == "otree":
        pass
    elif foc_sex == "otree_nonbinary":
        data = data[data.sex != 0]
    elif foc_sex == "prolific_only":
        sex_dic = {"Male": 2, "Female": 1}
        data = data.replace({"Sex": sex_dic})
        data["sex"] = data["Sex"]
        data = data[~data.sex.isna()]
    elif foc_sex == "prolific_otree_same":
        sex_dic = {"Male": 2, "Female": 1}
        data = data.replace({"Sex": sex_dic})
        data = data[data["sex"] == data["Sex"]]
    else:
        raise Exception(f"{foc_sex} is not defined!")

    data_preserve_2 = data.copy(deep=True)
    for foc_mig in ["otree", "prolific_only", "prolific_adds_otree", "prolific_otree_same"]:
        data = data_preserve_2.copy(deep=True)

        if foc_mig == "otree":
            pass
        elif foc_mig == "prolific_only":
            data.loc[data['Country of birth'] != "Germany", "migration_bg"] = 1
            data.loc[data['Country of birth'] == "Germany", "migration_bg"] = 0
        elif foc_mig == "prolific_adds_otree":
            data.loc[data['Country of birth'] != "Germany", "migration_bg"] = 1
        elif foc_mig == "prolific_otree_same":
            data = data[~((data['Country of birth'] != "Germany") & (data['migration_bg'] == 0))]
        else:
            raise Exception(f"{foc_mig} is not defined!")

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
        ai_pred_wtp_stage, wtp_stage_step_size = [], []
        for i, p in df.iterrows():
            if p.tasks_order == 0:
                ai_pred_wtp_stage.append(credit_data.iloc[p.lender_row]["pred_"])
                wtp_stage_step_size.append(10)
            elif p.tasks_order == 1:
                ai_pred_wtp_stage.append(
                    round((immo_data.iloc[p.apartment_row]["pred_price"] - 300_000) / 40_000) * 40_000 + 300_000)
                wtp_stage_step_size.append(40_000)
            else:
                raise Exception(f"Check tasks_order = {p.tasks_order} of index {p.index}.")
        df["ai_pred_wtp_raw"] = ai_pred_wtp_stage
        df["wtp_stage_step_size"] = wtp_stage_step_size

        # get predictions "normalized" (on steps)
        df["ai_pred_wtp"] = df["ai_pred_wtp_raw"].copy(deep=True)
        df.loc[df["wtp_stage_step_size"] == 40_000, "ai_pred_wtp"] = df["ai_pred_wtp"] - 300_000
        df["ai_pred_wtp"] = df["ai_pred_wtp"] / df["wtp_stage_step_size"]

        data_preserve_3 = df.copy(deep=True)
        for with_neg_wtp in [True, False]:
            df = data_preserve_3.copy(deep=True)

            if not with_neg_wtp:
                df = df[df.wtp >= 50]

            data_preserve_4 = df.copy(deep=True)
            for with_dev0 in [True, False]:
                df = data_preserve_4.copy(deep=True)

                # get WOA and WTP developer characteristics
                social_char_dict = {
                    "eher links": 2, "mitte": 5, "eher rechts": 8,
                    "ja": 1, "nein": 0,
                    "divers": 0, "weiblich": 1, "männlich": 2}
                wtp_dev = [dev_data.iloc[i] for i in df["dev_row1"]]
                df["wtp_dev_sex"] = [social_char_dict[wtp_dev[i]["gender"]] for i in range(0, len(wtp_dev))]
                df["wtp_dev_migration"] = [social_char_dict[wtp_dev[i]["migrant"]] for i in range(0, len(wtp_dev))]
                df["wtp_dev_pol"] = [social_char_dict[wtp_dev[i]["politics"]] for i in range(0, len(wtp_dev))]

                if not with_dev0:
                    df = df[df["dev_row1"] != 0]

                # TODO: get median splits both ways

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

                # social distance ranks
                df["soc_dis_wtp_rank_t1"] = 15 - (df["soc_distance_t1_1"] + df["soc_distance_t1_2"] + df["soc_distance_t1_3"])
                df["soc_dis_wtp_rank_t1"] = normalize_col(df["soc_dis_wtp_rank_t1"])

                # social distance custom weighted
                importances = ["importance_sex", "importance_migration_bg", "importance_pol_views"]
                for i, singular_distance in enumerate(["sex_dis_wtp", "mig_dis_wtp", "pol_median_dis_wtp"]):
                    if "pol" in singular_distance:
                        df["pol_median_dis_wtp"] = (df.pol_dis_wtp > df.pol_dis_wtp.quantile()).replace({True: 1, False: 0})
                    df.loc[df[singular_distance] == 1, singular_distance + "_w2"] = df[singular_distance] - (
                                5 - df[importances[int(i / 2)]]) / 9
                    df.loc[df[singular_distance] == 0, singular_distance + "_w2"] = df[singular_distance] + (
                                5 - df[importances[int(i / 2)]]) / 9
                df["soc_dis_wtp_w2"] = normalize_col(df["sex_dis_wtp_w2"] + df["mig_dis_wtp_w2"] + df["pol_median_dis_wtp_w2"])

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

                # write results in data frame
                for measure in ["soc_dis_wtp", "soc_dis_wtp_w", "soc_dis_wtp_w2", "soc_dis_ranked_wtp"]:
                    results_frame.loc[r_i, "sex_preproc"] = foc_sex
                    results_frame.loc[r_i, "mig_preproc"] = foc_mig
                    results_frame.loc[r_i, "with_neg_wtp"] = int(with_neg_wtp)
                    results_frame.loc[r_i, "with_dev0"] = int(with_dev0)
                    results_frame.loc[r_i, "n"] = len(df)

                    results_frame.loc[r_i, "measure"] = measure
                    for treat in ["none", "dev", "acc", "both"]:
                        df_t = df[df.treatment == treat]
                        foc_median = np.median(df_t[measure])

                        # median with smaller or equal
                        low_seq = df_t[df_t[measure] <= foc_median].wtp
                        up_seq = df_t[df_t[measure] > foc_median].wtp
                        difference_seq = up_seq.mean() - low_seq.mean()
                        pval_seq = mannwhitneyu(low_seq, up_seq).pvalue
                        results_frame.loc[r_i, treat + "_med_seq_diff"] = difference_seq
                        results_frame.loc[r_i, treat + "_med_seq_diff_pval"] = pval_seq

                        # median with larger or equal
                        low_leq = df_t[df_t[measure] < foc_median].wtp
                        up_leq = df_t[df_t[measure] >= foc_median].wtp
                        difference_leq = up_leq.mean() - low_leq.mean()
                        pval_leq = mannwhitneyu(low_leq, up_leq).pvalue
                        results_frame.loc[r_i, treat + "_med_leq_diff"] = difference_leq
                        results_frame.loc[r_i, treat + "_med_leq_diff_pval"] = pval_leq

                        # correlation
                        results_frame.loc[r_i, treat + "_corr"] = df_t[["wtp", measure]].corr().values[0][1]
                    r_i += 1

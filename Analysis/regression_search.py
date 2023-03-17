import pandas as pd
import statsmodels.api as sm
import itertools
import warnings
warnings.filterwarnings("ignore", message="In a future version of pandas all arguments of concat except for the argument 'objs' will be keyword-only")

# Range of values for the parameters of our search
data_preproc = ["sex_mig_prolific", "raw", "mig_prolific", "sex_prolific", "sex_only_bin", "sex_mig_prolific", "sexonlybin_mig_prolific",
                "sexonlybin_sex_prolific", "sexonlybin_sex_mig_prolific"]
soc_dis_measure = ["aggregated", "aggregated weighted", "single", "single weighted rel", "single weighted abs"]
reg_errors = ["robust", "dev_cluster", "task_cluster", "dev_task_cluster", "stage_cluster", "dev_stage_cluster"]
reg_equation = ["wtp", "woa", "guess_2_sticky_pred", "guess_2_pred_only"]
data_subset = [["none"], ["dev"], ["dev", "none"]]

# Get all combinations of parameters
row_combinations = list(itertools.product(data_preproc, soc_dis_measure, reg_errors))
col_combinations = list(itertools.product(reg_equation, data_subset))

# results frame
results = pd.DataFrame(columns=["wtp_none", "wtp_dev", "wtp_treateff", "woa_none",
                                "woa_dev", "woa_treateff",
                                "g1_sticky_none", "g1_sticky_dev", "g1_sticky_treateff",
                                "g1_predonly_none", "g1_predonly_dev", "g1_predonly_treateff",])

# Set up OLS regression for each combination
for params_row in row_combinations:
    results_for_row = []
    print(params_row[0])

    for params_col in col_combinations:
        # read in data
        data = pd.read_csv("Data/Versions/data_" + params_row[0] + ".csv")

        # Subset data (dev, none, or treatment effect)
        data = data[data.treatment.isin(params_col[1])]

        # Omit NaN in case of WOA
        if params_col[0] == "woa":
            data = data[~data.woa.isna()]

        # Define social distance(s)
        focal_stage = "wtp" if params_col[0] == "wtp" else "woa"
        if params_row[1] == "aggregated":
            focal_social_distance = ["soc_dis_" + focal_stage]
        elif params_row[1] == "aggregated weighted":
            focal_social_distance = ["soc_dis_" + focal_stage + "_w"]
        elif params_row[1] == "single":
            focal_social_distance = [el + focal_stage for el in ["sex_dis_", "mig_dis_", "pol_dis_"]]
        elif params_row[1] == "single weighted rel":
            focal_social_distance = [el + focal_stage for el in ["w_sex_", "w_mig_", "w_pol_"]]
        elif params_row[1] == "single weighted abs":
            focal_social_distance = [el + focal_stage + "_w" for el in ["sex_dis_", "mig_dis_", "pol_dis_"]]
        else:
            raise Exception(f"{params_row[1]} is not a valid parameter.")

        # Define the dependent variable
        if "guess_2" in params_col[0]:
            y = data["guess_2_woa"]
        else:
            y = data[params_col[0]]

        # Define independent variables of interest
        X = data[[]]
        X = sm.add_constant(X)

        # ...treatment dummy
        data["treat_dev"] = (data.treatment == "dev").astype(int)
        if len(params_col[1]) == 2:
            X["treat_dev"] = data["treat_dev"]

        # ...social distance measure
        for soc_dis_meas in focal_social_distance:
            # for all reg equations
            X[soc_dis_meas] = data[soc_dis_meas]
            if len(params_col[1]) == 2:
                X["x_dev_" + soc_dis_meas] = data["treat_dev"] * data[soc_dis_meas]
            # for reg eq based on guess 2
            if "guess_2" in params_col[0]:
                X["pred"], X["prior"] = data["ai_pred_woa"], data["guess_1_woa"]
                X["x_pred_" + soc_dis_meas] = data["ai_pred_woa"] * data[soc_dis_meas]
                if len(params_col[1]) == 2:
                    X["x_dev_pred_" + soc_dis_meas] = data["treat_dev"] * X["x_pred_" + soc_dis_meas]
            # for reg eq based on guess 2 and stickiness of prior
            if "sticky" in params_col[0]:
                X["x_prior_" + soc_dis_meas] = data["guess_1_woa"] * data[soc_dis_meas]
                if len(params_col[1]) == 2:
                    X["x_dev_prior_" + soc_dis_meas] = data["treat_dev"] * X["x_prior_" + soc_dis_meas]

        # Define the remaining independent variables (controls)
        # ...participant attributes
        X["sex"], X["migration_bg"], X["pol_views"], X["age"] = data["sex"], data["migration_bg"], data["pol_views"], data["age"]
        # ...developer fixed effects
        if focal_stage == "wtp":
            data['dev_row'] = data['dev_row1']
        elif focal_stage == "woa":
            data['dev_row'] = data['dev_row2']
        else:
            raise Exception(f"{focal_stage} not a valid focal stage.")
        dev_dummies = pd.get_dummies(data.dev_row, drop_first=True)
        X["dev_1"], X["dev_2"] = dev_dummies[1], dev_dummies[2]
        # ...task and stage fixed effects
        X["tasks_order"], X["stage_order"] = data["tasks_order"], data["stage_order"]
        # importances controls
        if params_row[1] in ["aggregated weighted", "single weighted rel", "single weighted abs"]:
            X["importance_sex"], X["importance_migration_bg"], X["importance_pol_views"] = \
                data["importance_sex"], data["importance_migration_bg"], data["importance_pol_views"]

        # marker for debug
        # if params_col[0] == "guess_2_pred_only":
            # print("Here")
        if (params_col[0] == "woa") and ("none" in params_col[1]) and ("dev" in params_col[1]) and (params_row[0] == "sex_mig_prolific") and (params_row[1] == "single weighted abs") and (params_row[2] == "dev_task_cluster"):
            print("Our current version!")

        # Fit OLS regression
        if params_row[2] == "robust":
            model = sm.OLS(y, X).fit(cov_type='HC1')
        elif params_row[2] == "dev_cluster":
            model = sm.OLS(y, X).fit(cov_type='cluster', cov_kwds={'groups': data['dev_row']}, use_t=True)
        elif params_row[2] == "task_cluster":
            model = sm.OLS(y, X).fit(cov_type='cluster', cov_kwds={'groups': data['tasks_order']}, use_t=True)
        elif params_row[2] == "dev_task_cluster":
            data["dev_task_group"] = data["dev_row"].astype(str) + data["tasks_order"].astype(str)
            model = sm.OLS(y, X).fit(cov_type='cluster', cov_kwds={'groups': data['dev_task_group']}, use_t=True)
        elif params_row[2] == "stage_cluster":
            model = sm.OLS(y, X).fit(cov_type='cluster', cov_kwds={'groups': data['stage_order']}, use_t=True)
        elif params_row[2] == "dev_stage_cluster":
            data["dev_stage_group"] = data["dev_row"].astype(str) + data["stage_order"].astype(str)
            model = sm.OLS(y, X).fit(cov_type='cluster', cov_kwds={'groups': data['dev_stage_group']}, use_t=True)

        # # Get regression result summary
        # model.summary()

        # # Get the coefficients
        # coefficients = model.params

        # Get relevant p values of social distance measures
        all_p_val = model.pvalues
        all_rel_p_val = []
        for soc_dis_meas in focal_social_distance:
            if len(params_col[1]) == 1:  # none or dev
                if "guess_2" not in params_col[0]:
                    all_rel_p_val.append(all_p_val[soc_dis_meas])
                if "guess_2" in params_col[0]:
                    all_rel_p_val.append(all_p_val["x_pred_" + soc_dis_meas])
                if "sticky" in params_col[0]:
                    all_rel_p_val.append(all_p_val["x_prior_" + soc_dis_meas])
            else:  # treatment effect
                if "guess_2" not in params_col[0]:
                    all_rel_p_val.append(all_p_val["x_dev_" + soc_dis_meas])
                if "guess_2" in params_col[0]:
                    all_rel_p_val.append(all_p_val["x_dev_pred_" + soc_dis_meas])
                if "sticky" in params_col[0]:
                    all_rel_p_val.append(all_p_val["x_dev_prior_" + soc_dis_meas])

        # None and dev: get smallest; Treatment effect: get smallest interaction
        smallest_p_val = min(all_rel_p_val)

        # Append to row results
        results_for_row.append(smallest_p_val)

    # Append to results frame
    results.loc[str(params_row)] = results_for_row



# results = results[(results.wtp_none > 0.1) & (results.wtp_dev < 0.1) & (results.wtp_treateff < 0.1)]
# len(results)
results.to_csv("Data/results_reg_search.csv")
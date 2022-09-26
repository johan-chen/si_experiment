import pandas as pd

prolific_data = pd.read_csv("Data/prolific_export_si1.csv").append(
    pd.read_csv("Data/prolific_export_si2.csv"))

experiment_data = pd.read_csv("Data/all_apps_wide_2022-09-16.csv")
experiment_data = experiment_data[experiment_data["participant.label"].isin(prolific_data["Participant id"])]

immo_data = pd.read_csv("Frontend/Data/immonet_data_selected.csv")
credit_data = pd.read_csv("Frontend/Data/lending_data_selected.csv")

relevant_task_correct = []
for i in range(0, len(experiment_data)):
    foc_exp = experiment_data.iloc[i]
    if foc_exp["participant.task_payment_relevance"] + foc_exp["participant.stage_order"] == 2:  # the second rel_task_name presented to participant is relevant
        if foc_exp["participant.tasks_order"] + foc_exp["participant.stage_order"] == 1:  # this second rel_task_name is the lending rel_task_name
            rel_task_name = "lending"
            if foc_exp["participant.tasks_order"] == 1:  # lending rel_task_name is saved in revision2
                relevant_estimate = foc_exp["si_experiment.1.player.revision2"]
            else:  # lending rel_task_name is saved in revision
                relevant_estimate = foc_exp["si_experiment.1.player.revision"]
        else:  # this second rel_task_name is the immo rel_task_name
            rel_task_name = "immo"
            if foc_exp["participant.tasks_order"] == 1:  # immo rel_task_name is saved in revision
                relevant_estimate = foc_exp["si_experiment.1.player.revision"]
            else:  # immo rel_task_name is saved in revision2
                relevant_estimate = foc_exp["si_experiment.1.player.revision2"]

    else:  # the first rel_task_name presented to participant is relevant
        if foc_exp["participant.tasks_order"] + foc_exp["participant.stage_order"] == 1:  # this first rel_task_name is the immo rel_task_name
            rel_task_name = "immo"
            if foc_exp["participant.tasks_order"] == 1:  # immo rel_task_name is saved in revision
                relevant_estimate = foc_exp["si_experiment.1.player.revision"]
            else:  # lending rel_task_name is saved in revision2
                relevant_estimate = foc_exp["si_experiment.1.player.revision2"]
        else:  # this first rel_task_name is the lending rel_task_name
            rel_task_name = "lending"
            if foc_exp["participant.tasks_order"] == 1:  # lending rel_task_name is saved in revision2
                relevant_estimate = foc_exp["si_experiment.1.player.revision2"]
            else:  # lending rel_task_name is saved in revision
                relevant_estimate = foc_exp["si_experiment.1.player.revision"]

    if rel_task_name == "lending":
        row = foc_exp["participant.lender_row"]
        true_val = credit_data.iloc[row]["y_"]
    else:
        row = foc_exp["participant.apartment_row"]
        true_val = immo_data.iloc[row]["price"]
        true_val = round((true_val - 300_000) / 40_000) * 40_000 + 300_000

    relevant_task_correct.append(true_val == relevant_estimate)

experiment_data["relevant_task_correct"] = relevant_task_correct

# experiment_data[
#     (experiment_data["participant.label"].isin(pd.read_csv("Data/prolific_export_si2.csv")["Participant id"])) &
#     (experiment_data["participant.var_payment_amount"] > 0)
#     ][["participant.label", "participant.var_payment_amount"]].to_csv("participants_to_pay_2nd_exp.csv")

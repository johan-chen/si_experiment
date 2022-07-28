import sys
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, r2_score

# path (python console vs. terminal)
path_pre = ""
if len(sys.argv) > 1:
    if sys.argv[1] == "0":
        path_pre = "../"
        print("Pre-path appended.")

# seed
np.random.seed(0)

# write selection to file?
write_selected_file = False

# get immo data
data = pd.read_csv(path_pre + "LendingTask/PoolOfObs_Lending_R2_97.csv", sep=";")

# number of bins
n_b = 21

# accuracy (i.t.o. hit rate on 20/25 original bins)
hit_rate = np.sum(data.pred_ == data.y_)/len(data)
print(f"In the data, originally, {round(hit_rate, 4)*100}% of the observations are predicted correctly "
      f"(26 unq bins pred y, 20 unq bins true y).")

# accuracy (i.t.o. hit rate on n_b/n_b original bins)
data.pred_ = [int((x/26)*n_b) + np.random.binomial(1, 1 - ((x/26)*n_b) % 1) for x in data.pred_]
data.y_ = [int((x/26)*n_b) + np.random.binomial(1, 1 - ((x/26)*n_b) % 1) for x in data.y_]
data = data[data.pred_ != n_b]
hit_rate = np.sum(data.pred_ == data.y_)/len(data)
print(f"In the data, merged/cut to {n_b} bins, {round(hit_rate, 4)*100}% of the observations are predicted correctly.")

# # compute new accuracy: split first bin to yield 21 bins and get hit rate
# data.loc[data.y_ == 1, "y_"] = [np.random.binomial(1, 0.5) for i in range(0, np.sum(data.y_ == 1))]
# data.loc[data.pred_ == 1, "pred_"] = [np.random.binomial(1, 0.5) for i in range(0, np.sum(data.pred_ == 1))]

# test scores
mse = mean_squared_error(data.y_, data.pred_)
r_sq = r2_score(data.y_, data.pred_)
print("R^2: %.2f" % r_sq)
print("MSE: %.2f" % mse)
print("RMSE: %.2f" % (mse ** (1 / 2.0)))

# select data for frontend (broad range of values and representative w.r.t. hit rate)
data_selected = data.iloc[18:27, ].copy(deep=True)

# prepare selected data for frontend
home_ownership_dic = {'MORTGAGE': 'Hypothek', 'RENT': 'zur Miete', 'OWN': 'Eigentum', 'ANY': 'Sonstiges'}
purpose_dic = {'debt_consolidation': 'Schuldenkonsolidierung', 'credit_card': 'Kreditkarte',
               'home_improvement': 'Haus Sanierung/Ausbau', 'medical': 'Gesundheit (medizinische Gründe)',
               'major_purchase': 'größere Anschaffung', 'moving': 'Umzug', 'other': 'Sonstiges',
               'vacation': 'Urlaub', 'house': 'Hauskauf', 'small_business': 'Kleinunternehmen',
               'car': 'Auto', 'renewable_energy': 'Erneugerbare Energien', 'wedding': 'Hochzeit',
               'educational': 'Bildung'}
job_new_dic = {'Sales': 'Vertrieb', 'IT': 'IT', 'Supervisor': 'Führungskraft', 'Management position': 'Management',
               'Other': 'Sonstiges', 'Accountant': 'Buchaltung', 'Nurse': 'Krankenpflege', 'Teacher': 'Lehrkraft',
               'Office worker': 'Bürokraft', 'Technician': 'Techniker/in', 'Operations': 'Operativer Bereich',
               'Truck driver': 'Fernfahrer/in', 'Project management': 'Projektmanagement', 'Administration': 'Verwaltung',
               'Customer service': 'Kundenservice', 'Consultant': 'Unternehmensberatung', 'Analyst': 'Analyst',
               'store manager': 'Filialleiter/in', 'Engineer': 'Ingenieur/in', 'Self-employed': 'Selbstständig',
               'Police': 'Polizei', 'Mechanic': 'Mechaniker/in', 'Marketing': 'Marketing', 'Warehousing': 'Lagerhaltung',
               'Therapist': 'Therapeut/in', 'Paralegal': 'Paralegal', 'Secretary': 'Serkretär/in'}
data_selected.replace({"home_ownership": home_ownership_dic, "purpose": purpose_dic, "job_new": job_new_dic}, inplace=True)
max_val = np.max([np.max(data["pred_"]), np.max(data["y_"])])
data_selected.loc[:, "pred_"] = data["pred_"]*(100/max_val)
data_selected.loc[:, "y_"] = data["y_"]*(100/max_val)

# write selected data to file
if write_selected_file:
    data_selected.to_csv(path_pre + "Frontend/Data/lending_data_selected.csv")

import sys
import xgboost as xgb
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score, KFold, GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score

# path (python console vs. terminal)
path_pre = ""
if len(sys.argv) > 1:
    if sys.argv[1] == "0":
        path_pre = "../"
        print("Pre-path appended.")

# if trained on subset range only (FFM + within bounds of slider)
train_on_subset = True
tune_fresh = False
write_selected_file = False
city = "Berlin"  # Frankfurt

# random seed
rnd_state = 0
np.random.rand(rnd_state)

# get immo data
model_data = pd.read_csv(path_pre + "RealEstate/immonet_data_preprocessed.csv")

# parameters
test_size = 0.1
lower_bound, upper_bound = 300_000, 700_000
step_size = (upper_bound-lower_bound)/10

# subsetting if applicable
subset_str = ""
if train_on_subset:
    model_data = model_data[(model_data[city] == 1) & (lower_bound <= model_data.price) & (model_data.price <= upper_bound)]
    subset_str = subset_str + "_subset_" + city + "_only"  # _subset_ffm_only

# train test split
train, test = train_test_split(model_data, test_size=test_size, random_state=rnd_state)
# separate sets
xtrain, ytrain, xtest, ytest = train.drop(columns=["price"]), train["price"], test.drop(columns=["price"]), test["price"]

# get XGBoost Regressor
pred_model = xgb.XGBRegressor(verbosity=0)
if tune_fresh:
    search_grid = {'n_estimators': [250, 500, 1000, 2000], 'max_depth': [2, 4, 6], 'subsample': [.5, .75, 1],
                   'learning_rate': [.001, 0.01, .1, .5], 'random_state': [rnd_state]}
    grid_search = GridSearchCV(estimator=pred_model, param_grid=search_grid, n_jobs=3)
    grid_search.fit(xtrain, ytrain)
    file = open(path_pre + "RealEstate/xgboost_param" + subset_str + ".txt", "w+")
    file.write(str(grid_search.best_params_))
    params = grid_search.best_params_
    file.close()
else:
    params_file = open(path_pre + "RealEstate/xgboost_param" + subset_str + ".txt", "r")
    params = eval(params_file.read())  # read parameters from file
    params_file.close()
# set parameters
pred_model.set_params(**params)
# train model
pred_model.fit(xtrain, ytrain)
# get R^2
score = pred_model.score(xtrain, ytrain)
print("Training score: ", score)

# get k-fold cv average score
kfold = KFold(n_splits=5, shuffle=True)
kf_cv_scores = cross_val_score(pred_model, xtrain, ytrain, cv=kfold, scoring="r2")
print("K-fold CV average score: %.2f" % kf_cv_scores.mean())

# test scores
ypred = pred_model.predict(xtest)
mse = mean_squared_error(ytest, ypred)
r_sq = r2_score(ytest, ypred)
print("R^2: %.2f" % r_sq)
print("MSE: %.2f" % mse)
print("RMSE: %.2f" % (mse ** (1 / 2.0)))

# selected city prediction
foc_data = model_data[(model_data[city] == 1) & (lower_bound <= model_data.price) & (model_data.price <= upper_bound)]
foc_pred = pred_model.predict(foc_data.drop(columns=["price"]))
model_data.loc[model_data[city] == 1, "pred_price"] = foc_pred

# how many hits?
correct_indices = foc_data[(foc_data.price / step_size).round() * step_size == (foc_pred / step_size).round() * step_size].index
print(f"Number of times the prediction hits the correct, rounded step (steps in {step_size}):\n"
      f"{len(correct_indices)} hits out of {len(foc_data)}.")
r_sq_foc = r2_score(foc_data["price"], foc_pred)
print("R^2: %.2f" % r_sq_foc)
foc_test_indices = test[test.index.isin(foc_data.index)].index
correct_test_indices = correct_indices[correct_indices.isin(foc_test_indices)]
print(f"A total of {len(correct_test_indices)} out of {len(foc_test_indices)} were hit in the test data.")

# make real estate selection an write to file
n_correct_selec = int(1+10*len(correct_test_indices)/len(foc_test_indices))
indices_to_select = correct_test_indices[0:n_correct_selec]
false_test_indices = foc_test_indices[~foc_test_indices.isin(correct_test_indices)]
indices_to_select = indices_to_select.append(false_test_indices[30:(40-n_correct_selec)])

# prepare selected data for frontend
model_data.rename(columns={'floor (storey)': 'floor', 'nmbr of rooms': 'n_rooms',
                           'construction year': 'construction_year',
                           'Anteil Gruenenwaehler': 'share_green'}, inplace=True)
for int_col in ['floor', 'construction_year', 'n_rooms', 'sq_meters']:
    model_data[int_col] = model_data[int_col].astype(int)
for bool_col in ['garden', 'basement', 'elevator', 'balcony']:
    model_data[bool_col] = ["Ja" if b_c == 1 else "Nein" for b_c in model_data[bool_col]]
for ord_col in ['unemployment', 'share_green']:
    model_data[ord_col] = ["Unterdurchschnittlich" if o_c == 1 else "Durchschnittlich" if o_c == 2 else
    "Überdurchschnittlich" for o_c in model_data[ord_col]]

# write selected data to file
if write_selected_file:
    model_data[model_data.index.isin(indices_to_select)].to_csv(path_pre + "Frontend/Data/immonet_data_selected.csv")

import pandas as pd
import statsmodels.api as sm

# read in data
data = pd.read_csv("Data/data_raw.csv")
data = data[data.treatment.isin(["dev", "none"])]
data["dev"] = (data.treatment == "dev").astype(int)

# Define the dependent variable and independent variables
y = data['wtp']
X = data[['dev', 'soc_dis_wtp', 'sex', 'migration_bg', 'pol_views']]

# Group dev and task order for clustering of standard errors
data["devtask_group"] = data["dev_row1"].astype(str) + data["tasks_order"].astype(str)

# Create interaction terms
X = sm.add_constant(X)
X['x_dev_soc_dis_woa'] = X['dev'] * X['soc_dis_wtp']

# Fit the OLS regression model
model = sm.OLS(y, X).fit()
model = sm.OLS(y, X).fit(cov_type='HC1')
model = sm.OLS(y, X).fit(cov_type='cluster', cov_kwds={'groups': data['devtask_group']}, use_t=True)



# Get the p-values associated with the coefficients
p_values = model.pvalues

# Get the coefficients
coefficients = model.params
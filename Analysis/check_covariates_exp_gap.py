import pandas as pd

# read in data
data = pd.read_csv("Data/data_all.csv")
data = data[data.treatment == "acc"]

# risk
data["risk_aver_bin"] = pd.cut(data.risk_aver, bins=2, labels=[0,1])

for col in ["risk_aver_bin", "Sex",]:
    for foc_bin in [0, 1]:
        foc_data = data[data["risk_aver_bin"] == foc_bin]
        foc_data_neg_gap = foc_data[foc_data.expectation_gap_acc_woa < 0]
        foc_data_no_gap = foc_data[foc_data.expectation_gap_acc_woa == 0]
        foc_data_pos_gap = foc_data[foc_data.expectation_gap_acc_woa > 0]
        print(f"Bin {foc_bin} for {col}:")
        print(f"Neg Gap: mean woa = {foc_data_neg_gap.woa.mean()}, n = {len(foc_data_neg_gap)}, for Risk Aversion:")
        print(f"Neg Gap: mean woa = {foc_data_no_gap.woa.mean()}, n = {len(foc_data_no_gap)}, for Risk Aversion:")
        print(f"Neg Gap: mean woa = {foc_data_pos_gap.woa.mean()}, n = {len(foc_data_pos_gap)}, for Risk Aversion:")
        print("\n")




# get expectation gap
data.expectation_gap_acc_woa







for c in data.columns:
    print(c)
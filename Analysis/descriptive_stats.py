import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu
import statsmodels.api as sm
from Analysis.misc_methods import *

plt.style.use(["science", "grid"])

# import data
data = pd.read_csv("Data/data.csv")
data_dev = data[data.treatment.isin(["dev", "both"])]
data_dev_only = data[data.treatment == "dev"]
data_both_only = data[data.treatment == "both"]
data_no_dev = data[data.treatment.isin(["acc", "none"])]
data_none = data[data.treatment.isin(["none"])]

treatment_grps = ['none', 'dev', 'acc', 'both']
wtp_dic, woa_dic, woa_stage_rel_adj = {}, {}, {}
for tr in treatment_grps:
    print(f"Treatment group {tr}:")

    foc_wtp = data[data.treatment == tr]['wtp']
    wtp_dic[tr] = foc_wtp
    print(f"Average WTP: {foc_wtp.mean()}")
    foc_woa = data[data.treatment == tr]['woa'].dropna()
    woa_dic[tr] = foc_woa
    print(f"Average WOA (only WOA stage): {foc_woa.mean()}")
    foc_rel_adj = data[data.treatment==tr]['stage_woa_rel_adj']
    woa_stage_rel_adj[tr] = foc_rel_adj
    print(f"Average rel. adj. in WOA stage: {foc_rel_adj.mean()}")
    print("\n")

# boxplots woa
fig, ax = plt.subplots()
ax.set_title("WOA")
ax.boxplot(woa_dic.values())
ax.set_ylim(-1.5, 2.5)
ax.set_xticklabels(woa_dic.keys())
plt.show()

# boxplots wtp
fig, ax = plt.subplots()
ax.set_title("WTP")
ax.boxplot(wtp_dic.values())
ax.set_xticklabels(woa_dic.keys())
plt.show()

# density plot absolute adjustment of WOA estimates (in steps)
fig, ax = plt.subplots()
for tr in treatment_grps:
    print(tr)
    ax.plot(range(0, 10), [get_stage_woa_rel_adj(data, tr, i)*100 for i in range(0, 10)], label=tr)
ax.set_ylabel("Relative frequency [\%]")
ax.set_xlabel("Absolute adjustment [slider steps]\n(initial vs. final guess in WOA stage)")
ax.legend()
plt.tight_layout()
plt.savefig("Analysis/Plots/abs_adjustments_woa.pdf")

# bar plot WTP: avg social distance
plot_wtp = False
if plot_wtp:
    fig, ax = plt.subplots()
    data_dev = data[data.treatment.isin(["dev", "both"])]
    avg_dis_wtp, wtps = [], [20, 30, 40, 50, 60, 70, 80]
    for w in wtps:
        avg_dis_wtp.append(data_dev[data.wtp == w]["wtp_dev_distance_weighted"].mean())
    ax.bar(x=wtps, height=avg_dis_wtp, width=3)
    ax.set_ylabel("Weighted social distance")
    ax.set_xlabel("WTP: Choice of probability to see AI prediction [\%]")
    plt.tight_layout()
    plt.show()


# WTP and weighted social distance
for distance_type in ["wtp_dev_distance", "wtp_dev_distance_weighted", "wtp_soc_dist_rank_t1"]:
    print(f"\n\nDistance type \"{distance_type}\" with (0) treatment \"none\" "
          f"(1) treatment \"both\" and (2) \"both\" and \"dev\" and "
          f"(3) \"dev\" only.")
    for i, foc_data in enumerate([data_none, data_both_only, data_dev, data_dev_only,]):
        print(f"\n({i})")
        mask = foc_data[distance_type] >= np.median(data_dev[distance_type])
        foc_data_high = foc_data[mask]
        foc_data_low = foc_data[~mask]
        foc_data_high.woa.median()
        foc_data_low.woa.median()
        pval = round(mannwhitneyu(foc_data_high.wtp, foc_data_low.wtp).pvalue, 3)
        print(f"For higher soc. distance, average WTP is {round(np.nanmean(foc_data_high.wtp), 3)}, "
              f"median is {round(np.nanmedian(foc_data_high.wtp), 3)};\n"
              f"For lower soc. distance, average WTP is {round(np.nanmean(foc_data_low.wtp), 3)}, "
              f"median is {round(np.nanmedian(foc_data_low.wtp), 3)};\n"
              f"This difference is sign. with p-value {pval} (U-Test).")


# WOA and weighted social distance
for distance_type in ["woa_dev_distance", "woa_dev_distance_weighted", "woa_soc_dist_rank_t2"]:
    print(f"\n\nDistance type \"{distance_type}\" with (0) treatment \"none\" "
          f"(1) treatment \"both\" and (2) \"both\" and \"dev\" and "
          f"(3) \"dev\" only.")
    for i, foc_data in enumerate([data_none, data_both_only, data_dev, data_dev_only,]):
        print(f"\n({i})")
        mask = foc_data[distance_type] >= np.median(data_dev[distance_type])
        foc_data_high = foc_data[mask]
        foc_data_low = foc_data[~mask]
        foc_data_high.woa.median()
        foc_data_low.woa.median()
        pval = round(mannwhitneyu(foc_data_high.woa, foc_data_low.woa).pvalue, 3)
        print(f"For higher soc. distance, average WOA is {round(np.nanmean(foc_data_high.woa), 3)}, "
              f"median is {round(np.nanmedian(foc_data_high.woa), 3)};\n"
              f"For lower soc. distance, average WOA is {round(np.nanmean(foc_data_low.woa), 3)}, "
              f"median is {round(np.nanmedian(foc_data_low.woa), 3)};\n"
              f"This difference is sign. with p-value {pval} (U-Test).")


data_no_dev[["woa", "woa_dev_distance_weighted"]].corr()
plt.show()

# play around
data[(data.treatment == "dev") | (data.treatment == "both")][["wtp_dev_distance_weighted", "wtp"]].corr()
data[(data.treatment == "acc") | (data.treatment == "none")][["wtp_dev_distance_weighted", "wtp"]].corr()

plt.scatter(x=data[(data.treatment == "dev") | (data.treatment == "both")][["wtp_dev_distance_weighted"]],
            y=data[(data.treatment == "dev") | (data.treatment == "both")][["wtp"]])
plt.show()




install.packages('weights')
library('weights')

#
# read in dis data for correlation test
# _____________________________________
twitter_data = read.csv("../si_experiment/Data/twitter_data_20230317.csv")
twitter_data_subset = subset(twitter_data, select = c(negative_sentiment, avg_align))

weighted_corr = cov.wt(twitter_data_subset, wt = twitter_data$followers_count, cor = TRUE)
p_val_weighted_cor = wtd.cor(twitter_data_subset, weight = twitter_data$followers_count, bootse = TRUE, bootp = TRUE)$p.value

# Alexander Booth
# February 13, 2018

# A Normal Approximation of the Beta Distribution

#Reference:
#https://www.vosesoftware.com/riskwiki/NormalapproximationtotheBetadistribution.php

#Note: Approximation works best only when alpha & beta are >= 10

#Input, exact parameters of 2 Beta distribution
#Diff_est is the difference to estimate the difference of proportions
#Output is a 1 row dataframe, including normal parameters and estimate
#of Bayesian posterior probability
normal_approx <- function(alpha_a, beta_a,
                          alpha_b, beta_b, diff_est = 0) {
  #init results
  results <- matrix(NA, nrow=1, ncol=6)
  
  #Get Data
  set.seed(123)
  u1 <- alpha_a / (alpha_a + beta_a)
  u2 <- alpha_b / (alpha_b + beta_b)
  var1 <- alpha_a * beta_a / ((alpha_a + beta_a) ^ 2 * (alpha_a + beta_a + 1))
  var2 <- alpha_b * beta_b / ((alpha_b + beta_b) ^ 2 * (alpha_b + beta_b + 1))
  pB_better <- 1 - pnorm(diff_est, u2 - u1, sqrt(var1 + var2))
  pB_worse <- 1 - pB_better
  
  #Get Results
  results[1,] <- c(u1, var1, u2, var2, pB_better, pB_worse)
  results_df <- as.data.frame(results, stringsAsFactors = FALSE)
  colnames(results_df) <- c("Normal Mean A", "Normal Variance A", "Normal Mean B", "Normal Variance B",
                            "Probability B is Superior", "Probability B is Worse")
  return(results_df)
}

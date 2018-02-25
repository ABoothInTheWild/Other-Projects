#Alexander Booth

#This function calculates proabilities and expected change in success rates between two groups

#Successes and Failures should be lists of how many successes and failures there were per trial
#priors can be overwritten
bayesAnalysis <- function(a.successes, a.failures, b.successes, b.failures, 
                          prior_alpha = 1, prior_beta = 1){
  
    n.trials = 10000
    
    #init results
    results <- matrix(NA, nrow=1, ncol=15)
    
    #init prior
    #Use inputs or default to prior(1,1)
    prior.alpha <- prior_alpha
    prior.beta <- prior_beta
  
    #Get successes and failures
    a.group.success <- sum(a.successes)
    b.group.success <- sum(b.successes)
    a.group.failure <- sum(a.failures)
    b.group.failure <- sum(b.failures)
    
    #ensure reproducibility
    set.seed(123)
    
    #Sample from both posterior distributions
    a.samples <- rbeta(n.trials, a.group.success+prior.alpha, a.group.failure+prior.beta)
    b.samples <- rbeta(n.trials, b.group.success+prior.alpha, b.group.failure+prior.beta)
    
    #Get probability that Group 2 is superior
    p.b_superior <- sum(b.samples > a.samples)/n.trials
    p.b_worse <- 1 - p.b_superior
    
    #Get conversion rates
    a.est <- median(a.samples)
    b.est <- median(b.samples)
    
    a.quants <- quantile(a.samples, probs = c(0.05, 0.95))
    b.quants <- quantile(b.samples, probs = c(0.05, 0.95))
    
    #Get Diffs
    diff.b.a <- b.est-a.est
    diff.quants <- c(b.quants[1]-a.quants[2], b.quants[2]-a.quants[1])
    
    #Accumulate results
    results[1,] <- c(a.group.success, a.group.failure, b.group.success, b.group.failure,
                     a.est, a.quants[1], a.quants[2], b.est, b.quants[1], b.quants[2], diff.b.a, diff.quants[1], diff.quants[2],  
                     p.b_superior, p.b_worse)
    #Create Return DF
    results_df <- as.data.frame(results, stringsAsFactors = FALSE)
    colnames(results_df) <- c("Group 1 Successes", "Group 1 Failures", 
                              "Group 2 Successes", "Group 2 Failures", "A Success Probability", ".025 A Success",
                              ".975 A Success", "B Success Probability", ".025 B Success", ".975 B Success", "Change in Success B-A", 
                              ".025 Change in Success", ".975 Change in Success", "Probability Group 2 is Superior", "Probability Group 2 is Worse")
    
    return(results_df)
}

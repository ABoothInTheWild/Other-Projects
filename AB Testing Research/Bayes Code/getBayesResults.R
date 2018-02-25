#Alexander Booth
#Found Visualize

#This function calculates proabilities and expected change in success rates between two groups

#Full Data needs to have a Search_Result_Name, Group, and Success columns in scope
#Groups to Compare should be a vector of 2 groups, e.g. c(1,2), c(2,3), or c(1,3)
#NoWorseThanAPercent is only used in calculating the probability that B is superior or Worse than A
getBayesResults <- function(full_data, groupsToCompare, prior_alpha = 1, prior_beta = 1, 
                            noWorseThanAPercent = 1, splitBySearchResult = T){
  
  #Get all Search Result Names
  #Could instead use Ids here, as long as everything is unique
  #names <- matrix(unique(full_data$Search_Result_Name))
  names <- matrix(unique(full_data$Search_Result_IDs))
  iter <- length(names)
  
  if(!splitBySearchResult){
    iter <- 1
  }
  
  #init results
  results <- matrix(NA, nrow=iter, ncol=28)
  
  #init Monte Carlo Simulation trials
  #This is the same as approximating an integral
  n.trials <- 10000
  
  #init prior
  #Use inputs or default to prior(1,1)
  prior.alpha <- prior_alpha
  prior.beta <- prior_beta
  
  #iter through names
  for(n in 1:iter)
  {
    #get data
    se_rslt_name <- names[n]
    sub_data <- full_data[full_data$Search_Result_IDs == se_rslt_name,]
    
    if(!splitBySearchResult){
      sub_data <- full_data
    }
    
    #get total searches
    search_count <- nrow(sub_data)
    
    #Split by test group
    a.group.number <- groupsToCompare[1]
    b.group.number <- groupsToCompare[2]
    
    a.group <- sub_data[sub_data$Group == a.group.number,]
    b.group <- sub_data[sub_data$Group == b.group.number,]
    
    #Get successes and failures
    a.group.success <- sum(a.group$Success)
    b.group.success <- sum(b.group$Success)
    a.group.failure <- nrow(a.group) - a.group.success
    b.group.failure <- nrow(b.group) - b.group.success
    
    #ensure reproducibility
    set.seed(123)
    
    #Sample from both posterior distributions
    a.samples <- rbeta(n.trials, a.group.success+prior.alpha, a.group.failure+prior.beta)
    b.samples <- rbeta(n.trials, b.group.success+prior.alpha, b.group.failure+prior.beta)
    
    #Get probability that Group 2 is superior
    p.b_superior <- sum(b.samples > (a.samples * noWorseThanAPercent))/n.trials
    p.b_worse <- 1 - p.b_superior
    
    #Get conversion rates
    a.est <- median(a.samples)
    b.est <- median(b.samples)
    
    a.quants <- quantile(a.samples, probs = c(0.05, 0.95))
    b.quants <- quantile(b.samples, probs = c(0.05, 0.95))
    
    #Get Diffs
    diff.b.a <- b.est-a.est
    diff.quants <- c(b.quants[1]-a.quants[2], b.quants[2]-a.quants[1])
    
    #Get Customer Impact
    custImp <- search_count * diff.b.a
    custImp.quants <- c(search_count * diff.quants[1], search_count * diff.quants[2])
    
    #Get Ratio
    ratio <- b.samples/a.samples
    
    #Expected Percent Change in Success Rate
    delta.prob <- median(ratio)
    greater.prob <- median(ratio[ratio >= 1.0])
    less.prob <- median(ratio[ratio < 1.0])
    
    #Expected New Success Rate if B is deployed
    delta.est <- delta.prob * a.est
    delta.quants <- c(delta.prob*a.quants[1], delta.prob*a.quants[2])
    greater.est <- greater.prob * a.est
    less.est <- less.prob * a.est
    
    
    #Accumulate results
    results[n,] <- c(se_rslt_name, a.group.success, a.group.failure, b.group.success, b.group.failure, search_count, 
                     a.est, a.quants[1], a.quants[2], b.est, b.quants[1], b.quants[2], diff.b.a, diff.quants[1], diff.quants[2],  
                     p.b_superior, p.b_worse, custImp, custImp.quants[1], custImp.quants[2], delta.est, delta.quants[1], delta.quants[2],
                     greater.est, less.est, delta.prob * 100, greater.prob * 100, less.prob * 100)
  }
  
  #Create Return DF
  results_df <- as.data.frame(results, stringsAsFactors = FALSE)
  colnames(results_df) <- c("Search Result Name", "Group 1 Successes", "Group 1 Failures", 
                            "Group 2 Successes", "Group 2 Failures", "Search Count", "A Success Probability", ".025 A Success",
                            ".975 A Success", "B Success Probability", ".025 B Success", ".975 B Success", "Change in Success B-A", ".025 Change in Success", ".975 Change in Success", "Probability Group 2 is Superior", "Probability Group 2 is Worse",
                            "Change in Customer Success", ".025 Change in Customer Success", ".975 Change in Customer Success", "Expected New Success Rate If B is Deployed", ".025 Expected Success", ".975 Expected Success",
                            "Expected Rate if B is Better", "Expected Rate if B is Worse", "Expected Percent Change in New Success Rate If B is Deployed", "Percent Change if B is Better", "Percent Change if B is Worse")
  
  return(results_df)
}
# Alexander Booth
# June 8, 2018

# imports
library(ggplot2)

# Determine if a point lies within the unit circle
insidecircle <- function(x, y){
  rtnVal <- 0
  d <- sqrt(x^2 + y^2)
  
  if(d <= 1){
    rtnVal <- 1
  }
  return(rtnVal)
}

# function estimatepi that takes a single input N, generates N pairs of uniform
# random numbers and uses insidecircle to produce an estimate of pi.
# In addition to the estimate of pi, estimatepi also returns the standard error of this
# estimate, and a 95% confidence interval for the estimate.
# The function can also plot the points generated overlaying the unit circle
# input N = the number of darts to throw
estimatepi <- function(N, plotInd=FALSE){
  piEstimate <- 0
  piEstimate_SE <- 0
  piEstimate_05 <- 0
  piEstiamte_95 <- 0
  
  xSamples <- runif(N, -1, 1)
  ySamples <- runif(N, -1, 1)
  
  pointsInCircle <- c()
  
  for(i in 1:N){
    pointsInCircle = c(pointsInCircle, insidecircle(xSamples[i], ySamples[i]))
  }
  
  if(plotInd==TRUE){
    gg<-ggplot(data.frame(xSamples,ySamples, pointsInCircle), aes(x=xSamples, y=ySamples, color=as.factor(pointsInCircle))) + 
      geom_point() + scale_color_manual(values=c("red", "blue"))
    gg <- gg + vnl_theme() + coord_fixed() + theme(legend.position="none") +
      scale_fill_discrete(c("blue", "red")) + xlab("") + ylab("")
    gg <- gg + ggtitle(paste0(N, " Simulated Points in Unit Square/Circle to Estimate Pi"))
    gg<-gg+annotate("path",
                    x=0+1*cos(seq(0,2*pi,length.out=100)),
                    y=0+1*sin(seq(0,2*pi,length.out=100)),
                    size=2)
    print(gg)
  }
  
  p <- sum(pointsInCircle)/N
  piEstimate <- 4*p
  piEstimate_SE <- 4*sqrt((p*(1-p))/N)
  piEstimate_05 <- piEstimate - 1.96*piEstimate_SE
  piEstimate_95 <- piEstimate + 1.96*piEstimate_SE
  
  return(list(pi.est=piEstimate, pi.est.se=piEstimate_SE, pi.est.05=piEstimate_05, pi.est.95=piEstimate_95))
}

# Example Usage
estimatepi(500, plotInd=T)

# Run between 100 - 50,000 in increments of 50, storing estimates
# takes a year and a half to run
set.seed(123)

df <- data.frame(matrix(vector(), 0, 6,
                        dimnames=list(c(), c("pi.est", "pi.est.se", "pi.est.05", "pi.est.95", "N", "Diff"))),
                 stringsAsFactors=F)

for (i in seq(100, 50000, 50)){
  currEst <- estimatepi(i)
  df[nrow(df)+1,] <- c(unname(currEst), i, abs(pi - currEst$pi.est))
}

write.csv(df, file = "C:\\Users\\Alexander\\Documents\\baseball\\pi\\piEstimates.csv", 
          row.names = FALSE)

# Plot estimates versus pi
gg <- ggplot(data=df, aes(x=N, y=pi.est)) + geom_line(aes(group=1)) + 
  vnl_theme() + geom_hline(yintercept=pi, color="red") + xlab("Number of Darts Thrown") + ylab("Estimate of Pi") +
  ggtitle("Estimate of Pi for Number of Darts Thrown")
gg

# Calculate best version of N
N.Best <- df[df$Diff == min(df$Diff),"N"]
df[df$N == N.Best,]

# Use this best N to estimate pi 500 times
# By CLT, these should provide a distribution centered around pi
df2 <- data.frame(matrix(vector(), 0, 6,
                         dimnames=list(c(), c("pi.est", "pi.est.se", "pi.est.05", "pi.est.95", "Iter", "Diff"))),
                  stringsAsFactors=F)

for (i in seq(1, 500)){
  currEst <- estimatepi(N.Best)
  df2[nrow(df2)+1,] <- c(unname(currEst), i, abs(pi - currEst$pi.est))
}

# Plot the histogram, approximately normal due to CLT
gg<-ggplot(data.frame(df2$pi.est), aes(df2$pi.est)) + ylab("Density") + xlab("Simulated Estimates of Pi") + 
  geom_histogram(aes(y = ..density..), binwidth = 0.005, boundary = 0, closed = "left")
gg <- gg + vnl_theme()
gg <- gg + ggtitle(paste("Histogram for 500 Samples of Simulate Pi Estimates")) +
  stat_function(fun = dnorm, 
                args = list(mean(df2$pi.est), sd(df2$pi.est)), 
                lwd = 1.5, aes(colour = "Normal Approximation")) +
  scale_colour_manual("", values = c("blue")) + theme(legend.position="bottom")
gg

#See how it compares to the standard error and 95% CI recorded for best N
sample.sd <- sd(df2$pi.est)
abs(sample.sd - df[df$N == N.Best,]$pi.est.se) 

sum(df2$pi.est >= df[df$N == N.Best,]$pi.est.05 & 
      df2$pi.est <= df[df$N == N.Best,]$pi.est.95)/500

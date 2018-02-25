This is my research into the future of A/B Testing

The current popular methodology is to use classical frequentist methods to perform an AB test at one of the following levels, feature level or page level.

This has lead to a couple problems. The first comes in reaction to evaluating tests across many webpages or distinct individuals correctly. Unlike a feature level test, when you test many webpages at once you increase the likelihood that you get significant results as a fluke (see multiple comparisons problem https://en.wikipedia.org/wiki/Multiple_comparisons_problem). As a result, you have to adjust your threshold for your p-values to make sure the likelihood of a false positive on any of the pages or individuals you're testing is 5% (a common p-value threshold). This results in many fewer significant results (and sometimes none). I currently use the Holm-Bonferroni method (https://en.wikipedia.org/wiki/Holm%E2%80%93Bonferroni_method) to do this correction.

The second comes from the current velocity of a testing program. Most companies have a myriad number of ideas on how to improve webpages. However, the current A/B test setup forces these tests to be performed sequentially, severely limiting what they can test.


Bayesian methods in hypothesis testing should mitigate the first problem. One additional benefit of Bayesian hypothesis testing is that we can actually just treat the confidence as the likelihood of being correct, as opposed to the weird threshold interpretation you get with p-values. This could help in explaining our results to the business.

A Multi-Armed Bayesian Bandit could help with the second problem, while remaining statistically rigorous.

-Alexander Booth

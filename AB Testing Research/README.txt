This is my research into the future of A/B Testing

The current methodology is to use classical frequentist methods to perform an AB test at one of the following levels, feature level or page level.

This has lead to a couple problems. The first comes in reaction to a finding we had recently that we weren't evaluating our tests across many pages correctly. Unlike a feature level test, when we test many pages at once we increase the likelihood that we get significant results as a fluke (see multiple comparisons problem https://en.wikipedia.org/wiki/Multiple_comparisons_problem). As a result, we have to adjust our threshold for our p-values to make sure the likelihood of a false positive on any of the pages we're testing is 5% (our previous p-value threshold). This results in many fewer significant results (and sometimes none). We currently use the Holm-Bonferroni method (https://en.wikipedia.org/wiki/Holm%E2%80%93Bonferroni_method) to do our correction.

The second comes from the current velocity of our testing program. We have a myriad number of ideas on how to improve landing pages. However, the current A/B test setup forces these tests to be performed sequentially, severely limiting what we can test.



Bayesian methods in hypothesis testing should mitigate the first problem. One additional benefit of Bayesian hypothesis testing is that we can actually just treat the confidence as the likelihood of being correct, as opposed to the weird threshold interpretation you get with p-values. This could help in explaining our results to the business.

A Multi-Armed Bayesian Bandit should help with the second problem, while remaining statistically rigorous.

-Alexander Booth
t2adb
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 30 18:42:10 2018

@author: Alexander
"""

#Graphing Beta Distribution Example

#Reference:
#https://docs.scipy.org/doc/scipy-0.15.1/reference/generated/scipy.stats.beta.html

from scipy.stats import beta
import matplotlib.pyplot as plt
import numpy as np

#Set seed, init plots, get beta parameters
np.random.seed(seed=12345)
fig, ax = plt.subplots(1, 1)
priorA = 13
priorB = 783

#Summary stats of distribution
mean, var, skew, kurt = beta.stats(priorA, priorB, moments='mvsk')

#Plot pdf
x = np.linspace(beta.ppf(0.001, priorA, priorB),
              beta.ppf(0.999, priorA, priorB), 1000)
ax.plot(x, beta.pdf(x, priorA, priorB),
         'b-', lw=1, alpha=1, label='beta pdf')

#Check pdf vs cdf
vals = beta.ppf([0.001, 0.5, 0.999], priorA, priorB)
print(np.allclose([0.001, 0.5, 0.999], beta.cdf(vals, priorA, priorB))) #True

#Make plot pretty
ax.legend(loc='best', frameon=False)
ax.set_xlim([0.0, 0.1])
ax.set_ylim([0, 99])
plt.title('Posterior - Beta(3,783)')
plt.ylabel('Density')
plt.xlabel('Success Rate')
plt.grid(b=True, which='major', color='gray', linestyle='--', alpha= 0.3)
plt.show()

r = beta.rvs(priorA, priorB, size=100000)
print(np.percentile(r, 2.5)*10000)
print(np.percentile(r, 97.5)*10000)
print(np.percentile(r, 10)*10000)
print(np.percentile(r, 90)*10000)
print(np.mean(r)*10000)
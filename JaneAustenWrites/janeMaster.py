# -*- coding: utf-8 -*-
"""
Created on Mon Sep 17 21:44:52 2018

@author: Alexander
"""

import os
os.chdir("C:/Users/Alexander/Documents/baseball/bot/Jane")

from JaneAustenWrites import *
from credentials_JaneA import *

jane = JaneAustenWrites(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET, FB_URL)

while True:
    jane.doAction()
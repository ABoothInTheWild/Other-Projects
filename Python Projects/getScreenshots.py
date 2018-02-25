# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 17:23:13 2017

@author: t2adb
"""

#Import Selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

#Other Imports
import os

#Set Dir
os.chdir("G:\Pics")
#Find PhantomJS (This will be our phantom browser)
#Download from the internet otherwise
PHANTOMJS_PATH = 'C:/phantomjs-2.1.1-windows/bin/phantomjs.exe'

##############################################################################

#Function to get Screenshot from url and window size
def getScreenShot_ByURLAndWindowSize(url, windowWidth, windowHeight, reverse = False):  
   
    #Determine Orientation
    orient = "wide"
    if windowHeight > windowWidth:
        orient = "long"
        
    #Init Driver    
    driver = webdriver.PhantomJS(executable_path=PHANTOMJS_PATH)
    driver.set_window_size(windowWidth, windowHeight) # set the window size that you need 
    driver.get(searchURL)     
    delay = 10 # seconds
    
    try:
        #Wait for MainContent to load
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'MainContent')))
        
        #If we have scroll, we want to reverse the browser size to fit the most content as possible
        #Only do this once
        scrollBarInd = driver.execute_script("return MainContent.scrollHeight>MainContent.clientHeight;")        
        if scrollBarInd and not reverse:
            getScreenShot_ByURLAndWindowSize(url, windowHeight, windowWidth, reverse = True)
        
        else: #Get screenshot
            driver.save_screenshot(searchTerm + "_" + orient + '.png')
    except TimeoutException:
        print("Loading main content took longer than 10 seconds for " + searchTerm)
    
    #Close Driver
    driver.close()
    
##############################################################################

#Get Search Result Names
text_file = open("K:/t2adb/intermediatePageSearchTerms.txt", "r")
searchRsltNames = text_file.read().splitlines()

#searchRsltNames = ["slotted screws"]

#Window Size
windowWidth = 1920
windowHeight = 1080

#Base URL, avoid ab test
url = 'https://www.mcmaster.com/?abtests=CLPvsBroad~~1#'

#Loop through search names and grab screenshots
for name in searchRsltNames:
    #replace spaces by dashes to create url for search term
    searchTerm = name.replace(" ", "-").lower()
    searchURL = url + searchTerm
    
    #Get Screenshot
    getScreenShot_ByURLAndWindowSize(searchURL, windowWidth, windowHeight)

# -*- coding: utf-8 -*-
"""
Created on Thu Dec 21 12:52:35 2017

@author: t2adb
"""

#Import Selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

#Find PhantomJS (This will be our phantom browser)
#Download from the internet otherwise
PHANTOMJS_PATH = 'C:/phantomjs-2.1.1-windows/bin/phantomjs.exe'     

#Window Size
windowWidth = 1920
windowHeight = 1080     

#Base URL
url = "https://www.mcmaster.com/#"     
partNumbers = ["92196a245"]  

#Loop through part numbers and grab specs from product detail
for number in partNumbers:
    searchURL = url + number
    
    driver = webdriver.PhantomJS(executable_path=PHANTOMJS_PATH)
    driver.set_window_size(windowWidth, windowHeight) # set the window size that you need 
    driver.get(searchURL)     
    delay = 5 # seconds  

    try:
        #Wait for Main Content to load
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'MainContent')))
        #Get Specs
        info = driver.find_elements_by_tag_name('td')
        for i in info:
            if i.text != '':
                print(i.text)  
            
    except TimeoutException:
        print("Loading main content took longer than 5 seconds for " + searchURL)
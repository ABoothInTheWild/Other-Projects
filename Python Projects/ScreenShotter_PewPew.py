# -*- coding: utf-8 -*-
"""
Created on Thu Dec 14 10:30:27 2017

@author: t2adb
"""

#Import Selenium
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

class ScreenShotter(object):
    
    def __init__(self, baseURL, picPath):
        self.baseURL = baseURL
        self.picPath = picPath
    
    #Function to get Screenshot by window size
    def getScreenShot_ByWindowSizeAndURL(self, windowW, windowH, url = ""):
        print("hello")
        #Get URL to screenshot. If none given, use base
        if url == "":
            url = self.baseURL
            
        #Determine Orientation
        orient = "wide"
        if windowH > windowW:
            orient = "long"
            
        #Init Driver
        driver = webdriver.PhantomJS(executable_path=PHANTOMJS_PATH)
        driver.set_window_size(windowW, windowH) # set the window size that you need 
        driver.get(url)     
        delay = 5 # seconds
        
        try:
            #Wait for MainContent to load
            WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'MainContent')))
            #Get screenshot
            driver.save_screenshot(self.picPath + url + "_" + orient + '.png')
            driver.quit()
            print("done")
        except Exception as e:
            print(e)
            print("Loading main content took longer than 5 seconds for " + url)
        driver.close()


from selenium import webdriver

#Find PhantomJS (This will be our phantom browswer)
PHANTOMJS_PATH = 'C:/phantomjs-2.1.1-windows/bin/phantomjs.exe'

#Init ScreenShotter Class
#Driver, BaseURL, Destination to save Images
screenShotter = ScreenShotter("https://www.mcmaster.com/", "G:/Pics/")

#Get Search Result Names
searchRsltNames = ["standard threaded rods"]

#Window Size
windowWidth = 1920
windowHeight = 1080

#Loop through search names and grab screenshots
for name in searchRsltNames:
    #replace spaces by dashes to create url for search term
    searchTerm = name.replace(" ", "-")
    searchURL = screenShotter.baseURL + "#" + searchTerm
    
    screenShotter.getScreenShot_ByWindowSizeAndURL(windowWidth, windowHeight, url = searchURL)
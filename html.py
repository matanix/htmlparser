
import urllib
import re
import json as simplejson
import datetime
import base64
import os.path
from os import listdir, makedirs
from os.path import isfile, join, exists
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import sys

import unittest, time, re

def selget(url):
    driver = webdriver.Firefox()
    driver.implicitly_wait(30)
    verificationErrors = []
    accept_next_alert = True
    driver = driver
    delay = 3
    driver.get(url)
   # driver.find_element_by_link_text("All").click()
    for i in range(1,3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(4)
    html_source = driver.page_source
    data = html_source.encode('utf-8')

    return data


###########################################FUNCTIONS######################################################
def getNewList(userUrl, pattern, nextPattern, add = True, isselget = False):
	#Parsing variables
	lastPage = False
	page = 1 
	content = ""
	newList = []

	if add == False:
		isselget = True

	#get the new list
	while lastPage != True:
		if add:
			#Calculate url by page
			url = userUrl
			url +=  "all?page="
			url += str(page)
			url += "&sort_by=best-selling"
		else:
			url = userUrl

		#Get the rows
		try:
			if isselget:
				print "selget"
				tempContent = selget(url)
			else:
				print "normal get"
				file = urllib.urlopen(url)
				tempContent = file.read()
				file.close()
		except:
			print "Probably wrong URL. quitting\n"
			raw_input("press any key to exit\n")
			exit()

		pageList = re.findall(pattern, tempContent)

		if 'items-product-title"></span>\n' in pageList:
			pageList.remove('product-title"></span>\n')

		newList += pageList

		#Check if last
		nextCheck = re.findall(nextPattern, tempContent)

		if len(nextCheck) == 0 or len(pageList) <= 4 or not add:
			lastPage = True

		page += 1

	return newList


def saveLog(newList, lastList, siteName, dateString, baseSiteUrl, namePattern):
	log = ""

	for newProduct in newList:

		#find the search link for the item
		searchLink = ""
		productName = re.search(namePattern, newProduct)

		if productName != None:
			productName = productName.group(0)[1:len(productName.group(0))-1]
			words = productName.split(' ')
			searchLink = baseSiteUrl + "search?q="
			for word in words:
				searchLink += word + "+"
			if searchLink[len(searchLink) - 1] == '+':
				searchLink = searchLink[0:len(searchLink) - 1]
		else:
			productName = "Name not found. notify matan please. info: " + newProduct + " "

		#check if new item
		if newProduct not in lastList:
			log += "product: "
			log += productName
			log += "\n"
			log += "newly added to spot (new best seller)" + str(newList.index(newProduct)) 
			log += "\n"
			if searchLink != "":
						log += "search link : {}\n\n".format(searchLink)

		#check if item upgraded in spot
		for lastProduct in lastList:
			if (newProduct == lastProduct) and (newList.index(newProduct) != lastList.index(lastProduct)):
				if (newList.index(newProduct) < lastList.index(lastProduct)):
					log += "product: "
					log += productName
					log += " changed from spot " + str(lastList.index(lastProduct)) 
					log += " to spot " + str(newList.index(newProduct))
					log += "\t (jumped {})".format(lastList.index(lastProduct) - newList.index(newProduct))
					log += "\n"
					if searchLink != "":
						log += "search link : {}\n\n".format(searchLink)

	#check if item removed
	for lastProduct in lastList:
		if lastProduct not in newList:
			productName = re.search(namePattern, lastProduct)

			if productName != None:
				productName = productName.group(0)[1:len(productName.group(0))-1]
			else:
				productName = "Name not found. notify matan please. info: " + newProduct + " "

			log += "product: "
			log += productName
			log += "\n"
			log += "was removed from the site (probably shit product eh?)\n\n"


	#check if need to create this date's dir
	
	logDir = "logs/" + dateString

	if not os.path.exists(logDir):
		os.makedirs(logDir)

	logFile = open(logDir + '/' + siteName, 'w')

	logFile.write(log)

	logFile.close()
######################################################################################


###########################SITES DATA#######################################
sites = {"lucidfashionshop" : "https://lucidfashionshop.com/collections/",
 		"thebohoboutique" : "https://thebohoboutique.com/collections/",
 		"ariavoss" : "https://ariavoss.com/collections/all-swimwear",
 		"blushque" : "https://www.blushque.com/collections/",
 		"bikinimas" : "https://bikinimas.com/collections/mas-summer",
 		"dreamclosetcouture" : "https://dreamclosetcouture.us/collections/"}

patterns = {"lucidfashionshop" : 'product[s]{0,1}[a-zA-Z0-9\-_\"></ =.]{1,40}title[a-zA-Z0-9\-_\"></ .=]{6,41}\n',
 		"thebohoboutique" : 'item[s]{0,1}[a-zA-Z0-9\-_\"></ =.]{2,40}title[a-zA-Z0-9\-_\"></ .= ]{6,41}\n',
 		"ariavoss" : 'product[s]{0,1}[a-zA-Z0-9\-_\"></ =.]{1,40}title[a-zA-Z0-9\-_\"></ .=]{6,41}\n',
 		"blushque" : 'product[s]{0,1}[a-zA-Z0-9\-_\"></ =.]{1,40}title[a-zA-Z0-9\-_\"></ .=]{6,41}\n',
 		"bikinimas" : 'product[s]{0,1}[a-zA-Z0-9\-_\"></ =.]{1,40}title[a-zA-Z0-9\-_\"></ .=]{6,41}\n',
 		"dreamclosetcouture" : 'product-card__name[a-zA-Z0-9\-_\"></ =.]{2,40}\n'}

nextPatterns = {"lucidfashionshop" : 'next',
 		"thebohoboutique" : 'next',
 		"ariavoss" : 'next',
 		"blushque" : 'next',
 		"bikinimas" : 'next',
 		"dreamclosetcouture" : 'next'}

namePatterns = {"lucidfashionshop" : '>[a-zA-Z \-0-9]*?<',
 		"thebohoboutique" : '>[a-zA-Z \-0-9]*?<',
 		"ariavoss" : '>[a-zA-Z \-0-9]*?<',
 		"blushque" : '\"[A-Za-z \-0-9]*?\\\"',
 		"bikinimas" : '>[a-zA-Z \-0-9]*?<',
 		"dreamclosetcouture" : '>[a-zA-Z \-0-9]*?<'}

toAdd = {"lucidfashionshop" : True,
 		"thebohoboutique" : True,
 		"ariavoss" : False,
 		"blushque" : True,
 		"bikinimas" : False,
 		"dreamclosetcouture" : True}
##############################################################################



#############################################################################
####################################CODE#####################################
#############################################################################
mypath = "data/"
files = [f for f in listdir(mypath) if isfile(join(mypath, f))]		

sitesToLog = []

#check if any data is missing
for siteName in sites.keys():
	if siteName not in files:
		print siteName + " data missing. gathering and saving now."
		newList = getNewList(sites[siteName], patterns[siteName], nextPatterns[siteName], add = toAdd[siteName])

		#store the missing data
		dataStore = open("data/" + siteName, 'w')
		simplejson.dump(newList, dataStore)
		dataStore.close()

	else:
		sitesToLog.append(siteName)



#calculate the data for this log's directory
dateString = "{date:%Y-%m-%d-%H-%M-%S}".format(date=datetime.datetime.now())

#save logs of comparison
for siteName in sitesToLog:
	print "doing log for " + siteName
	newList = getNewList(sites[siteName], patterns[siteName], nextPatterns[siteName], add = toAdd[siteName])
	dataStore = open("data/" + siteName, 'r')
	lastList = simplejson.load(dataStore)
	dataStore.close()

	saveLog(newList, lastList, siteName, dateString, sites[siteName][0:(len(sites[siteName]) - len("collections/"))], namePatterns[siteName])

raw_input("press any key to exit\n")
exit()






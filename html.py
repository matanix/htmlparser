
import urllib
import re
import json as simplejson
import datetime
import base64
import os.path
from os import listdir
from os.path import isfile, join


def getNewList(userUrl):
	#Parsing variables
	lastPage = False
	page = 1 
	content = ""
	newList = []

	#get the new list
	while lastPage != True:
		#Calculate url by page
		url = userUrl
		url +=  "all?page="
		url += str(page)
		url += "&sort_by=best-selling"

		#Get the rows
		try:
			file = urllib.urlopen(url)
		except:
			print "Probably wrong URL. quitting\n"
			raw_input("press any key to exit\n")
			exit()

		tempContent = file.read()

		pageList = re.findall('product[s]{0,1}[a-zA-Z0-9\-_\"></ =.]{1,40}title[a-zA-Z0-9\-_\"></ .=]{6,41}\n', tempContent)
		pageList += re.findall('item[s]{0,1}[a-zA-Z0-9\-_\"></ =.]{2,40}title[a-zA-Z0-9\-_\"></ .= ]{6,41}\n', tempContent)
		pageList += re.findall('product-card__name[a-zA-Z0-9\-_\"></ =.]{2,40}\n',tempContent)

		if 'items-product-title"></span>\n' in pageList:
			pageList.remove('product-title"></span>\n')

		newList += pageList
		print pageList

		#Check if last
		nextCheck = re.findall('next', tempContent)

		if len(nextCheck) == 0 or len(pageList) <= 4:
			lastPage = True

		page += 1

	return newList


def saveLog(newList, lastList, siteName, preference):
	log = ""

	for newProduct in newList:
		if newProduct not in lastList:
			log += "product:"
			log += newProduct
			log += "\n"
			log += "newly added to spot (new best seller)" + str(newList.index(newProduct)) 
			log += "\n"

		for lastProduct in lastList:
			if (newProduct == lastProduct) and (newList.index(newProduct) != lastList.index(lastProduct)):
				if (newList.index(newProduct) > lastList.index(lastProduct)):
					log += "product:"
					log += newProduct
					log += "changed from spot " + str(lastList.index(lastProduct)) 
					log += "to spot " + str(newList.index(newProduct))
					log += "\n\n"


	for lastProduct in lastList:
		if lastProduct not in newList:
			log += "product:"
			log += lastProduct
			log += "\n"
			log += "was removed from the site (probably shit product eh?)\n"


	#save log of comparison
	if preference == "1":
		logName =  siteName + '-' + 'history-vs-{date:%Y-%m-%d-%H-%M-%S}.txt'.format(date=datetime.datetime.now())
	else:
		logName = siteName + '-' + 'recent-vs-{date:%Y-%m-%d-%H-%M-%S}.txt'.format(date=datetime.datetime.now())

	logFile = open("logs/" + logName, 'w')
	logFile.write(log)


def saveAsLastData(lastFileName, newList):
	#Save the run as last data
	dataStore = open("data/" + lastFileName, 'w')
	simplejson.dump(newList, dataStore)
	dataStore.close()



userUrl = raw_input("Please enter the url you want information on or 0 to check all\n")

siteName = ""

if userUrl == "0":
	lastListExists = True
else:
	lastListExists = False
	siteName = re.search("//.*?\.", userUrl).group(0)

firstFileName = base64.b64encode(userUrl)
lastFileName = base64.b64encode(userUrl + "last")



#if os.path.isfile("data/" + firstFileName):
#	lastListExists = True

if not lastListExists:
	print "This is the first time you try the script on this site\n"
	print "No results will be created, there is nothing to compare yet\n"

else:
	preference = ""

	while preference != "1" and preference != "2" :
		print "Enter 1 for information since first data gathering\n"
		print "Enter 2 for information since last data gathering\n"
		preference = raw_input()

	mypath = "data/"
	onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]		

	for file in onlyfiles:
		name = base64.b64decode(file)
	
		if ("last" in name) and (preference == "2"): 
			name = name[0:len(name)-4]
			fileName = name
		elif (preference == "1") and ("last" not in name):
			fileName = name
		else:
			continue
		
		siteName = re.search("//.*?\.", fileName).group(0)

		newList = getNewList(name)

		#Get the first time data 
		dataStore = open('data/' + base64.b64encode(fileName), 'r')
		lastList = simplejson.load(dataStore)
		dataStore.close()
	
		saveLog(newList, lastList, siteName, preference)

		saveAsLastData(base64.b64encode(fileName + 'last'), newList)

	raw_input("press any key to exit\n")
	exit()




newList = getNewList(userUrl)

log = ""


#if first time, save also as first time
if not lastListExists:
	dataStore = open("data/" + firstFileName, 'w')
	simplejson.dump(newList, dataStore)
	dataStore.close()

saveAsLastData(lastFileName, newList)

raw_input("press any key to exit\n")








import urllib
import re
import json as simplejson
import datetime
import base64
import os.path

userUrl = raw_input("Please enter the url you want information on\n")

lastListExists = False

firstFileName = base64.b64encode(userUrl)
lastFileName = base64.b64encode(userUrl + "last")

if os.path.isfile("data/" + firstFileName):
	lastListExists = True

if not lastListExists:
	print "This is the first time you try the script on this site\n"
	print "No results will be created, there is nothing to compare yet\n"

else:
	preference = ""

	while preference != "1" and preference != "2":
		print "Enter 1 for information since first data gathering\n"
		print "Enter 2 for information since last data gathering\n"
		preference = raw_input()

	#history compare
	if preference == "1":
			#Get the first time data 
			dataStore = open("data/" + firstFileName, 'r')
			lastList = simplejson.load(dataStore)
			dataStore.close()
	#recent compare
	else:
			#Get the first time data 
			dataStore = open("data/" + lastFileName, 'r')
			lastList = simplejson.load(dataStore)
			dataStore.close()


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
		exit()

	tempContent = file.read()
	pageList = re.findall('<a href="/products/.*', tempContent)
	newList += pageList

	#Check if last
	nextCheck = re.findall('<span class="next">', tempContent)

	if len(nextCheck) == 0:
		lastPage = True

	page += 1

log = ""

#If there is last time data compare
if lastListExists:
	for newProduct in newList:
		if newProduct not in lastList:
			log += "product:"
			log += newProduct
			log += "\n"
			log += "newly added to spot (new best seller)" + str(newList.index(newProduct)) 
			log += "\n"

		for lastProduct in lastList:
			if (newProduct == lastProduct) and (newList.index(newProduct) != lastList.index(lastProduct)):
				log += "product:"
				log += newProduct
				log += "\n"
				log += "changed from spot " + str(lastList.index(lastProduct)) 
				log += "to spot " + str(newList.index(newProduct))
				log += "\n"

	for lastProduct in lastList:
		if lastProduct not in newList:
			log += "product:"
			log += lastProduct
			log += "\n"
			log += "was removed from the site (probably shit product eh?)\n"


	#save log of comparison
	if preference == "1":
		logName = 'history-vs-{date:%Y-%m-%d-%H-%M-%S}.txt'.format(date=datetime.datetime.now())
	else:
		logName = 'recent-vs-{date:%Y-%m-%d-%H-%M-%S}.txt'.format(date=datetime.datetime.now())

	logFile = open("logs/" + logName, 'w+')
	logFile.write(log)


#Save the run as last data
dataStore = open("data/" + lastFileName, 'w')
simplejson.dump(newList, dataStore)
dataStore.close()

#if first time, save also as first time
if not lastListExists:
	dataStore = open("data/" + firstFileName, 'w')
	simplejson.dump(newList, dataStore)
	dataStore.close()

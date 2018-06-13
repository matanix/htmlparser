import argparse
import urllib
import re
import json as simplejson
import datetime
import base64
import os.path

#Get the url to check
parser = argparse.ArgumentParser()
parser.add_argument("html", help="html page to check")
args = parser.parse_args()

lastListExists = False

htmlFileName = base64.b64encode(args.html)

if os.path.isfile(htmlFileName):
	lastListExists = True
	#Get the last time data if possible
	dataStore = open(htmlFileName, 'r')
	lastList = simplejson.load(dataStore)
	dataStore.close()



#Parsing variables
lastPage = False
page = 1 
content = ""
newList = []

while lastPage != True:
	#Calculate url by page
	url = args.html
	url +=  "all?page="
	url += str(page)
	url += "&sort_by=best-selling"
	print url

	#Get the rows
	file = urllib.urlopen(url)
	tempContent = file.read()
	pageList = re.findall('<a href="/products/.*', tempContent)
	newList += pageList

	#Check if last
	nextCheck = re.findall('<span class="next">', tempContent)

	if len(nextCheck) == 0:
		lastPage = True
		print "there were " + str(page) + "pages"

	page += 1

log = ""

#If there is last time data compare
if lastListExists:
	for newProduct in newList:
		for lastProduct in lastList:
			if (newProduct == lastProduct) and (newList.index(newProduct) != lastList.index(lastProduct)):
				log += "product:"
				log += newProduct
				log += "\n"
				log += "changed from spot " + str(lastList.index(lastProduct)) 
				log += "to spot " + str(newList.index(newProduct))
				log += "\n"

	#save log of comparison
	logName = '{date:%Y-%m-%d-%H-%M-%S}.txt'.format(date=datetime.datetime.now())
	logFile = open(logName, 'w+')
	logFile.write(log)


#Save the run as last data
dataStore = open(htmlFileName, 'w')
simplejson.dump(newList, dataStore)
dataStore.close()

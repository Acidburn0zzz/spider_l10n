import re

import urllib.robotparser
from urllib.parse import urlparse
import sys 
import string 



def isFetchable(pageURL, rp, agentName = 'TTS', domainLimit = 'http://ir.inf.ed.ac.uk'):
	
	#Test 1 : is the page outside the domain 
	if not(pageURL.startswith(domainLimit)) :
		#print("An out of domain link has been found")
		#print("The link is : "+pageURL)
		return False

	#Test 2 : is the page not allowed via robots.txt	
	if not(rp.can_fetch(agentName,pageURL)):
		return False

	return True
	


def getListLinks(contentStr):
	return re.findall('<a(?:.*?)href="(.*?)"(?:.*?)>(?:.*?)</a>', contentStr)
	

def computeDepth(absoluteURL):
	#How deep is our URL
	return str.count(urlparse(absoluteURL).path,"/")

		
		
def checkURL(url):
	
	return re.match("^(http://|https://){0,1}[A-Za-z0-9][A-Za-z0-9\-\.]+[A-Za-z0-9]\.[A-Za-z]{2,}[\43-\176]*$",url)



def readFile(filename):
	f = open(filename, 'r')
	try:
	    content = f.read()
	finally:
	    f.close()
	return content

def getContentInside(content): 
	return re.compile('<body(.*?)</body>', re.DOTALL).findall(content)

def hasBeenTranslated(content,targetLanguage):
	'''Change here for another setting
	in our case we check if the list "translation" has targetLanguage'''
	interestingPart = re.compile('(?<=\<form class="languages go" method="get" action="#">)(.*?)(?=</form\>)',re.DOTALL).findall(content)
	return (targetLanguage in interestingPart[0])

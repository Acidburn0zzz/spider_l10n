import re
import sys 
import string
import urllib.parse
import urllib.request
import heapq
import time
import os.path

#Other file
import function_crawler

if len(sys.argv)!=4:
	if (len(sys.argv)==2) and (sys.argv[1]=="resume"):
		print('Resuming previous crawl...')
	else:
		print('The first argument should be the source URL of the domain to analyze.')
		print('The second one is the name of the language (see hasBeenTranslated/isNotOrphan method)')
		print('The third is the crawl_delay in the robots.txt')
		exit() 


frontier = []
exploredPages = []
listePagesStatus =[]
listErrorPages=[]
counterNT=0 #Counter of non-translated pages
domainLimit=""
addressRobot=""
agentName = 'MDN_translation_analysis'
crawlDelay = 0
targetLanguage =""
rp=urllib.robotparser.RobotFileParser()

if(len(sys.argv)==4): #First run
	sourceURL = sys.argv[1]
	targetLanguage = sys.argv[2]
	crawlDelay = int(sys.argv[3])

	print('--------------------------------------')
	print('The origin URL address is :'+ sourceURL)
	print('The name of the agent is : '+agentName)
	print('--------------------------------------')

	tuple1 = (0,sourceURL)
	heapq.heappush(frontier,tuple1)
	domainLimit = urllib.parse.urlparse(sourceURL).scheme+"://"+urllib.parse.urlparse(sourceURL).netloc+urllib.parse.urlparse(sourceURL).path
	#Setting up robots according to robots.txt
	addressRobot=urllib.parse.urlparse(sourceURL).scheme+"://"+urllib.parse.urlparse(sourceURL).netloc+"/robots.txt"
	rp.set_url(addressRobot)
	rp.read()
else: #Resume a previous run
	#Check if there is the save file
	if not os.path.isfile("savedState.txt"):
		print('If you want to resume a previous crawl')
		print('be sure to have the save file. It should')
		print('be saved here under "savedState.txt"')
		exit()

	#We can continue everything seems ok
	dictoResult=function_crawler.loadState(frontier,exploredPages,listePagesStatus,listErrorPages,counterNT,domainLimit,addressRobot,crawlDelay,targetLanguage)
	frontier=dictoResult['frontier']
	exploredPages=dictoResult['exploredPages']
	listePagesStatus=dictoResult['listePagesStatus']
	listErrorPages=dictoResult['listErrorPages']
	counterNT=dictoResult['counterNT']
	domainLimit=dictoResult['domainLimit']
	addressRobot=dictoResult['addressRobot']
	crawlDelay=dictoResult['crawlDelay']
	targetLanguage=dictoResult['targetLanguage']
	rp.set_url(addressRobot)
	rp.read()

indexLoop=0
#Loop
while frontier :
	if (indexLoop % 100==0 and indexLoop>0): #Save
		function_crawler.saveState(frontier,exploredPages,listePagesStatus,listErrorPages,counterNT,domainLimit,addressRobot,crawlDelay,targetLanguage)
	#webpage to explore
	tupleCurrent = heapq.heappop(frontier)
	#The tuple is composed of score + url
	currentPageToExplore = tupleCurrent[1]
	if currentPageToExplore not in exploredPages:
		#Handle 404 error : make sure that connection was not interrupted to be certain of result consistency 
		try:
			urlRequest = urllib.request.urlopen(urllib.parse.quote_plus(currentPageToExplore,"/:"))
			#the input argument has to have the same scheme (e.g. http -> https won't work)
			#Cut the  URL with possible "?redirect"
			currentPageToExplore=urlRequest.geturl().split('?redirect')[0]
			if currentPageToExplore not in exploredPages:
				print('Page : '+currentPageToExplore)
				#get a list of things inside body	
				contentPage=urlRequest.read().decode('utf-8')
				listContent = function_crawler.getContentInside(contentPage)

				#loop (maybe many pairs of listContent... who knows)
				list_links = []
				for c in listContent:
					list_links += function_crawler.getListLinks(c)

				#Now we have every link : make them absolute considering the current webpage 
				#in case we may encounter other directories
				listAbsolute=[]	
				for link in list_links:
					link = urllib.parse.urljoin(currentPageToExplore,link)
					linkParseResult = urllib.parse.urlparse(link)
					#avoid anchor repetition
					link=linkParseResult.scheme+"://"+linkParseResult.netloc+linkParseResult.path
					listAbsolute.append(link)
				
				for i,link in enumerate(listAbsolute):
					#print(link)
					#Do we want to access this link ? (robots.txt+ inside the domain ?)
					if not function_crawler.isFetchable(link, rp, agentName, domainLimit):
						listAbsolute.remove(link)
						list_links.pop(i)
					
					#Is this link already known ?
					elif link in exploredPages or link==currentPageToExplore:
						listAbsolute.remove(link)
						list_links.pop(i)
						#Compute score 
					else:
						scoreLink = function_crawler.computeDepth(link)
						tupleScored = (scoreLink,link)
						#Already in the frontier ? 
						if tupleScored in frontier:
							listAbsolute.remove(link)
							list_links.pop(i)
						#Filter some links
						elif function_crawler.filteredLink(link):
							listAbsolute.remove(link)
							list_links.pop(i)	
						#Else add the tuple to the frontier
						else:
							heapq.heappush(frontier,tupleScored)
							#print "correct link added : "+link

				exploredPages.append(currentPageToExplore)
				print("Size frontier : "+str(len(frontier)))
				print("# of explored pages : "+str(len(exploredPages)))
				indexLoop=indexLoop+1
				#Is the current page translated ? 
				if function_crawler.hasBeenTranslated(contentPage,targetLanguage):
					listePagesStatus.append((currentPageToExplore,"translated"))
				else:
					print("non translated page found : "+currentPageToExplore)
					listePagesStatus.append((currentPageToExplore,"non-translated"))
					counterNT=counterNT+1
				#Wait because of crawl/delay and ratio/request as far as
				#we don't have multiple threads/crawlers
				time.sleep(crawlDelay)
		except (urllib.error.HTTPError,urllib.error.URLError):
			print("Urllib error (?Connection?):"+currentPageToExplore)
			listErrorPages.append(currentPageToExplore)
		except UnicodeEncodeError:
			print("Encoding error :"+currentPageToExplore)
			listErrorPages.append(currentPageToExplore)

'''for page in exploredPages:
	print(page)'''
#print(listePagesStatus)
function_crawler.saveFile(listePagesStatus,"log_crawl.txt")
function_crawler.saveFile(listErrorPages,"log_error_pages.txt")
print("Number of non-translated pages: "+str(counterNT))
print("Number of pages with error: "+str(len(listErrorPages)))
print("End of script : files saved under log_crawl.txt and log_error_pages.txt")




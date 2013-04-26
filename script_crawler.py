import re
import sys 
import string
import urllib.parse
import urllib.request
import heapq
import time


#Other file
import function_crawler

if len(sys.argv)!=4:
	print('The first argument should be the source URL of the domain to analyze.')
	print('The second one is the name of the language (see hasBeenTranslated method)')
	print('The third is the crawl_delay in the robots.txt')
	exit() 
sourceURL = sys.argv[1]
targetLanguage = sys.argv[2]
crawlDelay = int(sys.argv[3])

agentName = 'MDN_translation_analysis'

print('--------------------------------------')
print('The origin URL address is :'+ sourceURL)
print('The name of the agent is : '+agentName)
print('--------------------------------------')



#Initialize
frontier = []
tuple1 = (0,sourceURL)
heapq.heappush(frontier,tuple1)
exploredPages = []
listePagesStatus =[]
domainLimit = urllib.parse.urlparse(sourceURL).scheme+"://"+urllib.parse.urlparse(sourceURL).netloc
#Setting up robots according to robots.txt
rp=urllib.robotparser.RobotFileParser()
rp.set_url(domainLimit+"/robots.txt")
rp.read()

#Loop
while frontier :
	
	#webpage to explore
	tupleCurrent = heapq.heappop(frontier)
	#The tuple is composed of score + url
	currentPageToExplore = tupleCurrent[1]
	if currentPageToExplore not in exploredPages:
		print('Page is : '+currentPageToExplore)
		urlRequest = urllib.request.urlopen(currentPageToExplore)

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
			elif link in exploredPages:
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
			
				#Else add the tuple to the frontier
				else:
					heapq.heappush(frontier,tupleScored)
					#print "correct link added : "+link

		exploredPages.append(currentPageToExplore)
		print("Frontier is : "+str(len(frontier)))
		print("# of explored pages : "+str(len(exploredPages)))

		#Is the current page translated ? 
		if function_crawler.hasBeenTranslated(contentPage,targetLanguage):
			listePagesStatus.append((currentPageToExplore,"translated"))
		else:
			print("non translated page found : "+currentPageToExplore)
			listePagesStatus.append((currentPageToExplore,"non-translated"))

		#Wait because of crawl/delay and ratio/request as far as
		#we don't have multiple threads/crawlers
		time.sleep(crawlDelay)
	
for page in exploredPages:
	print(page)









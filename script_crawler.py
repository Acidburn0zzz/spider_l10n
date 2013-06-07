#!/usr/bin/env python
"""This script can be used to find non-translated pages on a domain from a 
crawl starting with a given URL."""

from sys             import argv
from urllib.parse    import urlparse, urljoin, quote_plus
from urllib.request  import urlopen
from urllib          import robotparser, error
from heapq           import heappush, heappop
from time            import sleep
from os              import path
#Other file
from function_crawler import (isFetchable,
                            getListLinks,
                            computeDepth,
                            filteredLink,
                            saveFile,
                            saveState,
                            loadState,
                            getContentInside,
                            hasBeenTranslated)


if len(argv)!=4:
    if (len(argv) == 2) and (argv[1] == "resume"):
        print('Resuming previous crawl...')
    else:
        print('The first argument is the source URL of the domain to analyze.')
        print('The second one is the name of the target language ')
        print('The third is the crawl_delay in the robots.txt')
        exit() 


frontier         = [] # Frontier of the graph to explore
exploredPages    = [] # Set of explored pages
listePagesStatus = [] # Set of tuples with pages and status
listErrorPages   = [] # List of pages with error
counterNT        = 0  # Counter of non-translated pages
domainLimit      = "" # Limit of the domain to explore
addressRobot     = "" # Address of the robots.txt file
agentName        = 'MDN_translation_analysis' #Name of the agent we will use
crawlDelay       = 0  # Delay between two crawls (see robots.txt)
targetLanguage   = "" # Language that we want to check if it is translated
rp               = robotparser.RobotFileParser() # I Robot

if(len(argv) == 4): #First run
    sourceURL = argv[1]
    targetLanguage = argv[2]
    crawlDelay = int(argv[3])

    print('--------------------------------------')
    print('The origin URL address is :'+ sourceURL)
    print('The name of the agent is : '+agentName)
    print('--------------------------------------')

    tuple1 = (0, sourceURL)
    heappush(frontier, tuple1)
    scheme = urlparse(sourceURL).scheme
    netloc = urlparse(sourceURL).netloc
    path = urlparse(sourceURL).path
    domainLimit = scheme+"://"+netloc+path
    #Setting up robots according to robots.txt
    addressRobot = scheme+"://"+netloc+"/robots.txt"
    rp.set_url(addressRobot)
    rp.read()
else: #Resume a previous run
    #Check if there is the save file
    if not path.isfile("savedState.txt"):
        print('If you want to resume a previous crawl')
        print('be sure to have the save file. It should')
        print('be saved here under "savedState.txt"')
        exit()

    #We can continue everything seems ok
    dictoResult = loadState(frontier, exploredPages, listePagesStatus, listErrorPages, counterNT, domainLimit, addressRobot, crawlDelay, targetLanguage)
    frontier = dictoResult['frontier']
    exploredPages = dictoResult['exploredPages']
    listePagesStatus = dictoResult['listePagesStatus']
    listErrorPages = dictoResult['listErrorPages']
    counterNT = dictoResult['counterNT']
    domainLimit = dictoResult['domainLimit']
    addressRobot = dictoResult['addressRobot']
    crawlDelay = dictoResult['crawlDelay']
    targetLanguage = dictoResult['targetLanguage']
    rp.set_url(addressRobot)
    rp.read()

indexLoop = 0
#Loop
while frontier :
    if (indexLoop % 100 == 0 and indexLoop>0): #Save
        saveState(frontier, exploredPages, listePagesStatus, listErrorPages, counterNT, domainLimit, addressRobot, crawlDelay, targetLanguage)
    #webpage to explore
    tupleCurrent = heappop(frontier)
    #The tuple is composed of score + url
    currentPageToExplore = tupleCurrent[1]
    if currentPageToExplore not in exploredPages:
        #Handle 404 error : make sure that connection was not interrupted to be certain of result consistency 
        try:
            quotedURL = quote_plus(currentPageToExplore, "/:")
            urlRequest = urlopen(quotedURL)
            #the input argument has to have the same scheme (e.g. http -> https won't work)
            #Cut the  URL with possible "?redirect"
            currentPageToExplore = urlRequest.geturl().split('?redirect')[0]
            if (currentPageToExplore not in exploredPages) and (currentPageToExplore.startswith(domainLimit)):
                print('Page : '+currentPageToExplore)
                #get a list of things inside body
                contentPage = urlRequest.read().decode('utf-8')
                listContent = getContentInside(contentPage)

                #loop (maybe many pairs of listContent... who knows)
                list_links = []
                for c in listContent:
                    list_links += getListLinks(c)

                #Now we have every link : make them absolute considering the current webpage 
                #in case we may encounter other directories
                listAbsolute = []    
                for link in list_links:
                    link = urljoin(currentPageToExplore, link)
                    linkParseResult = urlparse(link)
                    #avoid anchor repetition
                    link = linkParseResult.scheme+"://"+linkParseResult.netloc
                    link = link+linkParseResult.path
                    listAbsolute.append(link)
                for i, link in enumerate(listAbsolute):
                    #Do we want to access this link ? (robots.txt+ inside the domain ?)
                    if not isFetchable(link,  rp,  agentName,  domainLimit):
                        listAbsolute.remove(link)
                        list_links.pop(i)
                    #Is this link already known ?
                    elif link in exploredPages or link == currentPageToExplore:
                        listAbsolute.remove(link)
                        list_links.pop(i)
                    #Compute score 
                    else:
                        scoreLink = computeDepth(link)
                        tupleScored = (scoreLink, link)
                        #Already in the frontier ? 
                        if tupleScored in frontier:
                            listAbsolute.remove(link)
                            list_links.pop(i)
                        #Filter some links
                        elif filteredLink(link):
                            listAbsolute.remove(link)
                            list_links.pop(i)
                        #Else add the tuple to the frontier
                        else:
                            heappush(frontier, tupleScored)
                exploredPages.append(currentPageToExplore)
                print("Size frontier : "+str(len(frontier)))
                print("# of explored pages : "+str(len(exploredPages)))
                indexLoop = indexLoop+1
                #Is the current page translated ? 
                if hasBeenTranslated(contentPage, targetLanguage):
                    listePagesStatus.append((currentPageToExplore, "translated"))
                else:
                    print("non translated page found : "+currentPageToExplore)
                    listePagesStatus.append((currentPageToExplore, "non-translated"))
                    counterNT = counterNT+1
            #Wait because of crawl/delay and ratio/request as far as
            #we don't have multiple threads/crawlers
            sleep(crawlDelay)
        except (error.HTTPError, error.URLError):
            print("Urllib error (?Connection?):"+currentPageToExplore)
            listErrorPages.append(currentPageToExplore)
        except UnicodeEncodeError:
            print("Encoding error :"+currentPageToExplore)
            listErrorPages.append(currentPageToExplore)

#Transform listePagesStatus so that generate_html.py is ok
finalListStatus=[]
for tupleStatus in listePagesStatus:
    finalListStatus.append(tupleStatus[0]+", "+tupleStatus[1])
finalListStatus.sort(key=str.lower)
saveFile(finalListStatus,"log_crawl.txt")
saveFile(listErrorPages,"log_error_pages.txt")
print("Number of non-translated pages: "+str(counterNT))
print("Number of pages with error: "+str(len(listErrorPages)))
print("End of script : files saved under log_crawl.txt and log_error_pages.txt")




from re              import findall, match, search, compile,DOTALL
from heapq           import heappush
from urllib          import robotparser
from urllib.parse    import urlparse



def isFetchable(pageURL, rp, agentName, domainLimit):
    
    #Test 1 : is the page outside the domain 
    if not(pageURL.startswith(domainLimit)) :
        #print("An out of domain link has been found")
        #print("The link is : "+pageURL)
        return False

    #Test 2 : is the page not allowed via robots.txt    
    if not(rp.can_fetch(agentName, pageURL)):
        return False

    return True
    


def getListLinks(contentStr):
    return findall('<a(?:.*?)href="(.*?)"(?:.*?)>(?:.*?)</a>', contentStr)
    

def computeDepth(absoluteURL):
    #How deep is our URL
    return str.count(urlparse(absoluteURL).path, "/")

        
        
def checkURL(url):
    
    return match("^(http://|https://){0,1}[A-Za-z0-9][A-Za-z0-9\-\.]+[A-Za-z0-9]\.[A-Za-z]{2,}[\43-\176]*$",url)

def filteredLink(link):
    #Change here if another setting
    #Set of filters to implement
    test = ("$revision" in link)
    test = test or ("$history" in link)
    test = test or ("$edit" in link)
    test = test or ("$locale" in link)
    test = test or (link=="https://developer.mozilla.org/en-US/docs/new")
    return  test

def readFile(filename):
    f = open(filename, 'r')
    try:
        content = f.read()
    finally:
        f.close()
    return content

def saveFile(data, filename):
    string = ''
    array = []
    f = open(filename, 'w')
    try:
        if type(data) == type(string):
            f.write(data)
        if type(data) == type(array):
            for d in data:
                f.write(str(d) + '\n')
    finally:
        f.close()
def saveData(data, f):
    string = ''
    array = []
    if type(data) == type(string):
            f.write(data)
    if type(data) == type(array):
        for d in data:
            f.write(str(d) + '\n')

def saveState(frontier,exploredPages,listePagesStatus,listErrorPages,counterNT,domainLimit,addressRobot,crawlDelay,targetLanguage):

    f = open("savedState.txt", 'w')
    try:
        #Save frontier
        f.write("--Frontier--\n")
        saveData(frontier,f)
        #Save exploredPages
        f.write("--Explored pages--\n")
        saveData(exploredPages,f)
        #Save listePagesStatus
        f.write("--List of pages status--\n")
        saveData(listePagesStatus,f)
        #Save listeErrorPages
        f.write("--List of error pages--\n")
        saveData(listErrorPages,f)
        #Save counterNT
        f.write("--Counter of non-translated--\n")
        saveData(str(counterNT),f)
        #Save domainLimit
        f.write("\n--Limit of domain to crawl--\n")
        saveData(domainLimit,f)
        #Save addressRobot
        f.write("\n--Robots file address--\n")
        saveData(addressRobot,f)
        #Save crawlDelay
        f.write("\n--Crawl delay chosen--\n")
        saveData(str(crawlDelay),f)
        f.write("\n--Target language--\n")
        saveData(targetLanguage,f)
    finally:
        f.close()

def loadState(frontier,exploredPages,listePagesStatus,listErrorPages,counterNT,domainLimit,addressRobot,crawlDelay,targetLanguage):
    state=readFile("savedState.txt")
    #Load frontier
    listFrontier = search('--Frontier--\n(.*)--Explored pages--\n', state,DOTALL).group(1).split('\n')[:-1]
    frontier=[]
    for elem in listFrontier:
        score= int(elem[1:-2].split(",")[0])
        page= elem[1:-2].split(",")[1][2:]
        heapq.heappush(frontier,(score,page))
    exploredPages = search('--Explored pages--\n(.*)--List of pages status--\n', state,DOTALL).group(1).split('\n')[:-1] #list of links
    rawListePagesStatus = search('--List of pages status--\n(.*)--List of error pages--\n', state,DOTALL).group(1).split('\n')[:-1]
    listePagesStatus =[] #List of (link,status)
    for elem in rawListePagesStatus:
        link= elem[2:-2].split(",")[0][:-1]
        status= elem[2:-2].split(",")[1][2:]
        listePagesStatus.append((link,status))
    listErrorPages=search('--List of error pages--\n(.*)--Counter of non-translated--\n', state,DOTALL).group(1).split('\n')[:-1] #List of links
    counterNT=int(search('--Counter of non-translated--\n(.*)--Limit of domain to crawl--\n', state,DOTALL).group(1))
    domainLimit = search('--Limit of domain to crawl--\n(.*)\n--Robots file address--\n', state,DOTALL).group(1) #String (url)
    addressRobot = search('--Robots file address--\n(.*)\n--Crawl delay chosen--\n', state,DOTALL).group(1) #String (url)
    crawlDelay=int(search('--Crawl delay chosen--\n(.*)\n--Target language--\n', state,DOTALL).group(1))
    targetLanguage = search('--Target language--\n(.*)', state,DOTALL).group(1) #String 
    #Create Dict and add return
    dicoResult = dict()
    dicoResult.setdefault("frontier",frontier)
    dicoResult.setdefault("exploredPages",exploredPages)
    dicoResult.setdefault("listePagesStatus",listePagesStatus)
    dicoResult.setdefault("listErrorPages",listErrorPages)
    dicoResult.setdefault("counterNT",counterNT)
    dicoResult.setdefault("domainLimit",domainLimit)
    dicoResult.setdefault("addressRobot",addressRobot)
    dicoResult.setdefault("crawlDelay",crawlDelay)
    dicoResult.setdefault("targetLanguage",targetLanguage)
    return dicoResult

def getContentInside(content): 
    return compile('<body(.*?)</body>', DOTALL).findall(content)

def hasBeenTranslated(content, targetLanguage):
    '''Change here for another setting
    in our case we check if the list "translation" has targetLanguage'''
    interestingPart = compile('(?<=\<form class="languages go" method="get")(.*?)(?=</form\>)', DOTALL).findall(content)
    if len(interestingPart)>0:
        return (targetLanguage in interestingPart[0])
    else:
        return False

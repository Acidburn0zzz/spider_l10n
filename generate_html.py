#!/usr/bin/env python
"""This document generates a HTML report from the 
crawl results (stored in log_crawl.txt)"""

from datetime         import date
from function_crawler import readFile

#Settings
nameFileToRead = "log_crawl.txt"
baseAdress = "https://developer.mozilla.org/en-US/docs/"

#Read File
content = readFile(nameFileToRead).split('\n')
listTuples = []
for line in content:
    if not line == "":
        listTuples.append((line.split(", ")[0],line.split(", ")[1]))

#list subdirectories with more than 10 pages + nbTranslated & nbNonTr
listSub = [] 
oldSub = "/"
counter = 0
counterTranslated = 0
counterNonTranslated = 0
listTranslated = []
listNonTranslated = []
listTranslatedOthers = []
listNonTranslatedOthers = []
for (url, status) in listTuples:
    currSub = url.replace(baseAdress, '')
    decomp = currSub.split('/')
    if (len(decomp)>1):
        currSub=decomp[0]+'/'+decomp[1]
    else:
        currSub = decomp[0]
    if not currSub == oldSub:
        if counter > 10:
            listSub.append((oldSub, counterTranslated, counterNonTranslated, listTranslated, listNonTranslated))
        else:
            listTranslatedOthers = listTranslatedOthers+listTranslated
            listNonTranslatedOthers = listNonTranslatedOthers+listNonTranslated
        counter = 0
        counterTranslated = 0
        counterNonTranslated = 0
        oldSub = currSub
        listTranslated = []
        listNonTranslated = []
    counter = counter+1
    if status == "translated":
        counterTranslated = counterTranslated+1
        listTranslated.append(url)
    elif status == "non-translated":
        counterNonTranslated = counterNonTranslated+1
        listNonTranslated.append(url)

today = date.today()


print('''<!DOCTYPE html>
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <title>Crawl l10n MDN-docs (fr)</title>
        <link rel="stylesheet" href="css/style.css" type="text/css" media="screen, projection">
        <script type="text/javascript" src="js/jquery-1.4.2.min.js">
        </script>
        <script type="text/javascript" src="js/sorttable.js">
        </script>
        <script type="text/javascript" src="js/scripts.js">
        </script>
        </script>
    </head>
    <body>
        <h1><b>Crawl l10n MDN-docs (fr) '''+today.strftime("%d/%m/%y")+'''</b></h1>
        <div id="listContainer">
            <div class="listControl">
                <a id="expandList">Expand All</a>
                <a id="collapseList">Collapse All</a>
            </div>
            <ul id="expList">''')
for sub in listSub:
    print("\t\t\t\t<li>")
    print("\t\t\t\t"+sub[0]+':'+str(sub[2]+sub[1])+' pages ~'+str(round((float(sub[1])/float(sub[1]+sub[2]))*100.0))+"% translated")
    print("\t\t\t\t\t<ul>")
    print("\t\t\t\t\t\t<li>")
    print("\t\t\t\t\t\t non-translated :"+str(sub[2]))
    print("\t\t\t\t\t\t\t<ul>")
    for site in sub[4]:
        print("\t\t\t\t\t\t\t\t<li>")
        print("\t\t\t\t\t\t\t\t\t"+"<a href="+site+">"+site+"</a>")
        print("\t\t\t\t\t\t\t\t</li>")
    print("\t\t\t\t\t\t\t</ul>")
    print("\t\t\t\t\t\t</li>")
    print("\t\t\t\t\t\t<li>")
    print("\t\t\t\t\t\t translated :"+str(sub[1]))
    print("\t\t\t\t\t\t\t<ul>")
    for site in sub[3]:
        print("\t\t\t\t\t\t\t\t<li>")
        print("\t\t\t\t\t\t\t\t\t"+"<a href="+site+">"+site+"</a>")
        print("\t\t\t\t\t\t\t\t</li>")
    print("\t\t\t\t\t\t\t</ul>")
    print("\t\t\t\t\t\t</li>")
    print("\t\t\t\t\t</ul>")
    print("\t\t\t\t\t</li>")
print("\t\t\t\t\t<li>")
print("Other pages")
print("\t\t\t\t\t<ul>")

print("\t\t\t\t\t\t<li>")
print("\t\t\t\t\t\t non-translated :"+str(len(listNonTranslatedOthers)))
print("\t\t\t\t\t\t\t<ul>")
for site in listNonTranslatedOthers:
    print("\t\t\t\t\t\t\t\t<li>")
    print("\t\t\t\t\t\t\t\t\t"+"<a href="+site+">"+site+"</a>")
    print("\t\t\t\t\t\t\t\t</li>")
print("\t\t\t\t\t\t\t</ul>")
print("\t\t\t\t\t\t</li>")
print("\t\t\t\t\t\t<li>")
print("\t\t\t\t\t\t translated :"+str(len(listTranslatedOthers)))
print("\t\t\t\t\t\t\t<ul>")
for site in listTranslatedOthers:
    print("\t\t\t\t\t\t\t\t<li>")
    print("\t\t\t\t\t\t\t\t\t"+"<a href="+site+">"+site+"</a>")
    print("\t\t\t\t\t\t\t\t</li>")
print("\t\t\t\t\t\t\t</ul>")
print("\t\t\t\t\t\t</li>")

print("\t\t\t\t\t</ul>")
print("\t\t\t\t</li>")

print('''\t\t\t</ul>
        </div>
        <table id="main" class="sortable">
            <thead>
                <tr>
                    <th>Category</th>
                    <th>Total</th>
                    <th>Translated</th>
                    <th>Non-Translated</th>
                    <th>Percentage translated</th>
                </tr>
            </thead>''')
for sub in listSub:
    print("\t\t\t\t<tr>")
    print("\t\t\t\t\t<td>"+sub[0]+"</td>")
    print("\t\t\t\t\t<td>"+str(sub[2]+sub[1])+"</td>")
    print("\t\t\t\t\t<td>"+str(sub[1])+"</td>")
    print("\t\t\t\t\t<td>"+str(sub[2])+"</td>")
    print("\t\t\t\t\t<td>"+str(round((float(sub[1])/float(sub[1]+sub[2]))*100.0))+"</td>")
    print("\t\t\t\t</tr>")
print("\t\t\t</table>")
print('''
    </body>
</html>''')

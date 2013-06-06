spider_l10n
===========

This crawler can be used to check if pages of a site have been
translated or not.
It does not use any external libraries and works with Python 3. 
The syntax is the following : 

`python script_crawler.py url_of_site target_language crawl_delay`

(please follow the directives of robots.txt)

OR if a previous crawl ran over more than 100 pages

`python script_crawler.py resume`



Users can be interested in customizing the crawler by modifying (a
minima) the following methods of the function_crawler.py file :
- filteredLink (for the links that should not be used)
- hasBeenTranslated (to design the relevant test)

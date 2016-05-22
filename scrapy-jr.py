import urllib2
import sys
from bs4 import BeautifulSoup
import time
print "Hi! I'm Scrapy Jr. Let's get started..."
start_time = time.time()
#Chopping Ingredients
site = sys.argv[1]
buf = site.rsplit('/')
fname = buf[len(buf)-3] + '-' + buf[len(buf)-2]
if "app" in site :
    tagvar = "list_top"
    tagtype = "class"
    tag = "a"
    pgtype = 1
else :
    tagvar = "cntboxbody"
    tagtype = "class"
    tag = "div"
    pgtype = 0
print pgtype
req = urllib2.Request(site,headers={ 'User-Agent': 'Mozilla/5.0' })
text = urllib2.urlopen(req).read()
#Making Soup
soup = BeautifulSoup(text,"html.parser")
#Searching for Bugs
data = soup.findAll(tag,attrs={tagtype:tagvar})

print "Ok. I could connect and fetch some data (check debug-jr.xml if needed)"
dfile = open ("debug-jr.xml",'w')
dfile.write(str(data)+'\n')
dfile.close
#Remove Bugs from Soup
ofile = open(fname+'-'+'urls.txt','w')

if pgtype == 0 :
    print "This seems to be a product page"
    for div in data:
        links = div.findAll('a')
        for a in links:
            ofile.write(a['href']+'\n')
else :
    print "This seems to be an application page"
    for a in data:
        ofile.write(a['href']+'\n')
#Throw Bugs
ofile.close()
print "URL Database has been prepared"
#Crawl URL file
with open(fname+'-'+'urls.txt') as f:
    lines = f.read().splitlines()
f.close
f = open(fname+'-'+'urls.txt','w')
ofile = open(fname+'-'+'tabsinfo.txt','w')
cntr = 0
print "Ok. Time to get messy! I'm crawling the URL database...\nThis may take a while. Coffee, maybe?"
for line_url in lines:
    #Load all bugs onto new file
    cntr = cntr + 1
    ofile.write("=====Site=====\n")
    ofile.write(line_url + '\n')
    req_line = urllib2.Request(line_url,headers={ 'User-Agent': 'Mozilla/5.0' })
    text_l = urllib2.urlopen(req_line).read()
    soup_line = BeautifulSoup(text_l,"html.parser")
    data = soup_line.findAll('div',attrs={'id':'tab'})
    ofile.write("\n======Tab Names======\n")
    for li in data:
        spans = li.findAll('span')
        for span in spans:
            ofile.write(span.get_text().encode('utf-8')+'\n')
    ofile.write("\n======Tab Links======\n")
    cnt=1
    for div in data:
        links = div.findAll('a')
        for a in links:
            if cnt==1 :
                ofile.write(line_url + '\n')
                f.write(line_url + '\n')
                cnt = 0
                continue
            ofile.write(a['href']+'\n')
            f.write(a['href'] + '\n')
    ofile.write("=====Next Site======\n\n")
ofile.close
end_time = time.time()
print "I crawled " + str(cntr) + " URLs with no problem at all."
print "That was a ton of data..phew! \nAlso, FYI - I took {} seconds to finish this.".format(end_time - start_time)

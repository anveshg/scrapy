import urllib2
import sys
from bs4 import BeautifulSoup
import time
print "Hi! I'm Scrapy Sr. Let's get started..."
start_time = time.clock()
try :
    with open("urlbucket.txt") as f1:
        urlbucket = f1.readlines()
except :
    print "ERORR: I couldn't find a file called urlbucket.txt - Scrapy's got to eat :(\nMake one for me and try again!"
    exit()
pcntr = 0
acntr = 0
for uline in urlbucket:
    site = uline
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

    req = urllib2.Request(site,headers={ 'User-Agent': 'Mozilla/5.0' })
    text = urllib2.urlopen(req).read()
    #Making Soup
    soup = BeautifulSoup(text,"html.parser")
    #Searching for Bugs
    data = soup.findAll(tag,attrs={tagtype:tagvar})
    dfile = open ("debug-sr.xml",'a')
    dfile.write("\n------"+fname+"------\n")
    dfile.write(str(data)+'\n')
    dfile.write("\n------"+fname+"------\n\n\n")
    dfile.close
    #Remove Bugs from Soup
    ofile = open(fname+'-'+'urls.txt','w')
    if pgtype == 0 :
        pcntr = pcntr + 1
        for div in data:
            links = div.findAll('a')
            for a in links:
                ofile.write(a['href']+'\n')
    else :
        acntr = acntr + 1
        for a in data:
            ofile.write(a['href']+'\n')
    #Throw Bugs
    ofile.close()

    #Crawl URL file
    with open(fname+'-'+'urls.txt') as f:
        lines = f.read().splitlines()
    f.close
    f = open(fname+'-'+'urls.txt','w')
    ofile = open(fname+'-'+'tabsinfo.txt','w')
    for line_url in lines:
        #Load all bugs onto new file
        ofile.write("=====Site=====\n")
        ofile.write(line_url + '\n')
        req_line = urllib2.Request(line_url,headers={ 'User-Agent': 'Mozilla/5.0' })
        text_l = urllib2.urlopen(req_line).read()
        soup_line = BeautifulSoup(text_l,"html.parser")
        data = soup_line.findAll('div',attrs={'id':'tab'})
        ofile.write("\n-------Tab Names---------\n")
        for li in data:
            spans = li.findAll('span')
            for span in spans:
                ofile.write(span.get_text().encode('utf-8')+'\n')
        ofile.write("\n-------Tab Links---------\n")
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
f1.close
end_time = time.clock()
print "Processed " + str(acntr) + " Application Pages and " + str(pcntr) + " Product Pages in {} seconds".format(end_time - start_time)

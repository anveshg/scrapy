#!/usr/bin/python

'''

Example output:

'''

import urllib2
import sys
from bs4 import BeautifulSoup
import time
import argparse
import os
import re
import requests

__author__ = 'Anvesh Gopalam'
start_time = time.time()

#######################################################

#ProductTree URLs Selection
ptagtype = "div"
ptagattr = "class"
ptagattrname = "cntboxbody"

#Tabs Selection
ttagtype = "div"
ttagattr = "id"
ttagattrname = "tab"

#Apps Page Tree
atagtype = "li"
atagattr= "id"
atagattrname = re.compile("^appcateg_\d+")

#######################################################

#Parse Command Line Arguments
def get_args():
    # Assign description to the help doc
    parser = argparse.ArgumentParser(
        description='This script retrieves elements from a given URL or a file of URLs')
    # Add arguments
    parser.add_argument(
        '-t','--type', type=str, help='Enter the Input Type - file or url or h1', required=True)
    parser.add_argument(
        '-i','--input', type=str, help='Enter the Actual Input - filename or url with http', required=True)
    # Array for all arguments passed to script
    args = parser.parse_args()
    # Set Script Operation Mode and return mode and input
    if "file" in args.type.lower() :
        mode = 1
        fname = args.input
        return mode, fname
    elif "url" in args.type.lower() :
        mode = 2
        url = args.input
        if "http://" not in url:
            url = "http://" + url
        return mode, url
    elif "h1" in args.type.lower() :
        mode = 3
        fname = args.input
        return mode, fname
    else :
        print "Unknown Argument. Type --help to check what to use"
        exit ()

def clean404(dirtybucket,cleanfile,filename_404,filename_man):
    #Open Files and Read Input Files
    dcnt = 0
    cleanedFile = open(cleanfile,'w')
    file404 = open(filename_404,'w')
    manCheckFile = open(filename_man,'w')

    cleanedbucket = []

    #Start Cleaning
    for uline in dirtybucket:
        if uline == "#" : continue
        if "http:" not in uline :
            manCheckFile.write(uline)
            cleanedFile.write("\n")
            cleanedbucket.append("\n")
            print "Weird URL Caught - " + uline
            dcnt += 1
            continue
        site = uline
        try :
            r = requests.head(uline)
            if r.status_code == 404:
                file404.write(site)
                cleanedFile.write("\n")
                cleanedbucket.append("\n")
                print "404 - " + site
                dcnt += 1
            else :
                cleanedFile.write(site + "\n")
                cleanedbucket.append(site)
        except (requests.ConnectionError,requests.HTTPError,requests.Timeout,requests.TooManyRedirects) as e:
                manCheckFile.write(site)
                cleanedFile.write("\n")
                cleanedbucket.append("\n")
                print str(e) + " - " + site
                dcnt += 1
    #Close Files
    cleanedFile.close
    manCheckFile.close
    file404.close
    return cleanedbucket , dcnt

def checktaginfo(proc_mode):
    if proc_mode == "urls_primary_prd":
        return ptagtype,ptagattr,ptagattrname
    elif proc_mode == "urls_tab":
        return ttagtype,ttagattr,ttagattrname
    elif proc_mode == "urls_primary_apps":
        a = ""
        return atagtype,atagattr,atagattrname

def geth1s(urlbucket,h1sfileName,manFileHfileName):
    #Open Files and Read Input
    outputH1 = open(h1sfileName,'w')
    manfileH1 = open(manFileHfileName,'w')
    h1ctr = 0
    #Print H1s
    for uline in urlbucket:
        if uline == "\n" :
            continue
        site = uline
        try :
            req = requests.get(site)
        except :
            print "Failed to get H1: " +site
            manfileH1.write("---")
            manfileH1.write(str(site))
            manfileH1.write("---\n")
            outputH1.write("\n")
            continue
        line_url = req.content
        soup = BeautifulSoup(line_url,"html5lib")
        data = soup.select("h1")
        if not data:
            manfileH1.write("---")
            manfileH1.write(str(site))
            manfileH1.write(str(data))
            manfileH1.write("---\n")
            outputH1.write("\n")
        elif "/solution/" in site :
            temp = data[0].get_text().encode('utf-8')
            temp = temp.strip("\t")
            temp = " ".join(temp.split())
            outputH1.write(temp + "\n")
            h1ctr += 1
        else :
            try :
                temp = data[1].get_text().encode('utf-8')
                temp = temp.strip("\t")
                temp = " ".join(temp.split())
                outputH1.write(temp + "\n")
                h1ctr += 1
            except :
                temp = data[0].get_text().encode('utf-8')
                temp = temp.strip("\t")
                temp = " ".join(temp.split())
                outputH1.write(temp + "\n")
                h1ctr += 1
    #Close Files
    outputH1.close
    manfileH1.close
    return h1ctr


def single_url(indata,fname_prefix) :
    #Create Directories
    dir_name = os.getcwd() + "/" + fname_prefix
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    #Set Output File Names
    out_fileName = dir_name + "/" + fname_prefix + "_urls.txt"
    cleanOut_fileName = dir_name + "/" + fname_prefix + "_clean.txt"
    file404_fileName = dir_name + "/" + fname_prefix + "_404urls.txt"
    manFile_fileName = dir_name + "/" + fname_prefix + "_manualcheck_links.txt"
    debugFile1_fileName = dir_name + "/" + "_" + "_debug_urls_"+ fname_prefix
    debugFile2_fileName = dir_name + "/" + "_" + "_debug_tabs_"+ fname_prefix
    h1s_fileName = dir_name + "/" + fname_prefix + "_H1s.txt"
    manFileH_fileName = dir_name + "/" + fname_prefix + "_manualcheck_H1s.txt"

    #Counters
    urlctr = 0
    err404 = 0
    mancheck = 0

    #Open Files
    outputFile = open(out_fileName,"w")
    debugFile1 = open(debugFile1_fileName,"w")
    debugFile2 = open(debugFile2_fileName,"w")

    #Start Getting Preliminary URLs
    req = urllib2.Request(indata,headers={ 'User-Agent': 'Mozilla/5.0' })
    text = urllib2.urlopen(req).read()

    #Set Tag Parameters for BeautifulSoup to fetch all URLs
    if "app" in indata :
        proc_mode = "urls_primary_apps"
    else :
        proc_mode = "urls_primary_prd"
    tagtype, tagattr, attrname = checktaginfo(proc_mode)

    print "\nScanning Sidebar URLs..."

    urlbucket = []
    #Write Sidebar URLs and close

    #Make Soup and Publish Debug Data
    soup1 = BeautifulSoup(text,"html5lib")

    data1 = soup1.findAll(tagtype,attrs={tagattr:attrname})
    debugFile1.write(str(data1) + "\n")
    debugFile1.close
    for li in data1:
        links = li.findAll('a')
        for a in links:
            urlbucket.append(a['href'])

    sidesize = len(urlbucket)
    if not urlbucket:
        urlbucket.append(indata)
        print "Warning: There is no sidebar on this page! There may be tabs though."
    else:
         print "Successfully fetched the Sidebar URLs."
         print "There are " + str(sidesize) + " URLs to process."
         if((sidesize >30)):
             print "That's a lot. You should probably get Coffee :)"

    temp = urlbucket
    for url in temp:
        url = url.encode("utf-8")
    urlbucket = temp

    outputFile = open(out_fileName,"w")

    print "\nScanning all Sidebar links and populating Tab URLs..."

    dirtybucket = []
    #Fetch Tab Links
    for uline in urlbucket:
        if uline == "#" : continue
        if "/solution/" in uline :
            dirtybucket.append(uline)
            continue
        req_line = urllib2.Request(uline,headers={ 'User-Agent': 'Mozilla/5.0' })
        try :
            text_l = urllib2.urlopen(req_line).read()
        except :
            print uline
        #Set Tag Parameters for BeautifulSoup to fetch all URLs
        proc_mode = "urls_tab"
        tagtype, tagattr, attrname = checktaginfo(proc_mode)
        #Make Soup and Publish Debug Data
        soup2 = BeautifulSoup(text_l,"html5lib")
        data2 = soup2.findAll(tagtype,attrs={tagattr:attrname})
        debugFile2.write(str(data2) + "\n\n")
        #Get Tab Links and Write to File
        flag = 1
        for li in data2:
            links = li.findAll('a')
            for a in links:
                if flag == 1 :
                    flag = 0
                    outputFile.write(uline+"\n")
                    dirtybucket.append(uline)
                    continue
                else :
                    outputFile.write(a['href']+"\n")
                    dirtybucket.append(a['href'])
    outputFile.close
    debugFile2.close

    temp = dirtybucket
    for url in temp:
        url = url.encode("utf-8")
    dirtybucket = temp

    sidesize = len(dirtybucket)

    print "Successfully fetched " + str(sidesize) + " Tab URLs."

    print "\nChecking for 404 Erors..."

    #Call Function to Clean generated URLs
    cleanedbucket , discrepancies = clean404(dirtybucket,cleanOut_fileName,file404_fileName,manFile_fileName)

    temp = cleanedbucket
    for url in temp:
        url = url.encode("utf-8")
    cleanedbucket = temp

    print "Successfully cleaned 404 URLs from the good ones."
    print "There were " + str(discrepancies) + " discrepancies."

    print "\nGenerating H1 List..."

    #Call Function to Get H1s
    hctr = geth1s(cleanedbucket,h1s_fileName,manFileH_fileName)

    print "Successfully fetched " + str(hctr) + " H1s."

    return

def multiple_urls(indata):
    try :
        with open(indata) as f1:
            processqueue = f1.readlines()
    except :
        print "ERORR: I couldn't find a file called " + infile
        exit()
    print "Found " + str(len(processqueue)) + " URLs to process.\n"
    for item in processqueue:
        buf = item.rsplit('/')
        fname_prefix = buf[len(buf)-3] + '-' + buf[len(buf)-2]
        print "\n----\nProcessing - " + item
        single_url(item,fname_prefix)

    return


#Main part of the code
mode, indata = get_args()

print "Alright, Let's get started"

if mode == 1 :
    multiple_urls(indata)
elif mode == 2 :
    buf = indata.rsplit('/')
    fname_prefix = buf[len(buf)-3] + '-' + buf[len(buf)-2]
    single_url(indata,fname_prefix)
elif mode == 3 :
    buf = indata.rsplit('.')
    fname_prefix = buf[-2]
    h1s_fileName = fname_prefix + "_H1s.txt"
    with open(indata) as f1:
        urlbucket = f1.readlines()
    #Call Function to Get H1s
    hctr = geth1s(cleanedbucket,fname_prefix,dir_name)

end_time = time.time()
print "Processed in {} seconds".format(end_time - start_time)

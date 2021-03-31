#https://api.elsevier.com/content/search/scopus?query=DOI(10.1016/j.stem.2011.10.002)+OR+DOI(10.1098/rsbl.2011.0293)&field=citedby-count,prism:doi&apiKey=7f59af901d2d86f78a1fd60c1bf9426a
import requests
from pprint import pprint
import json
from getxml import getxml
import time
import os

def getrefs(doi):

    key = "b6039e6ff3cd83f0fcd426ac57cfabe5"
    url = 'https://api.elsevier.com/content/search/scopus'
    contenturl = "https://api.elsevier.com/content/abstract/doi/" + doi

    head = {"Accept": "application/json", "X-ELS-APIKey": key}
    data = {'apiKey': key,"view": "REF"}


    # get references
    x = requests.request("GET", contenturl, headers=head,params=data)
    if x.status_code == 200:
        data = x.json()
        print()
    else:
        print(x.status_code)
        print(x.text)
        raise Exception("error the status code is not 200")
    try:
        referencelist = data["abstracts-retrieval-response"]["references"]["reference"]
    except:
        return False
    doilist = []
    for reference in referencelist:
        try:
            doilist.append(reference[r"ce:doi"])
        except:
            pass
    # get figures

    return doilist
# ( "Water gas shift"  AND  catalysis )  AND  ( activity )

def search(query, amount):
    key = "b6039e6ff3cd83f0fcd426ac57cfabe5"
    citeurl = "http://api.elsevier.com/content/search/scopus"

    start = 0
    data = {'apiKey': key, "query": query, "cursor": "*", "field": "citedby-count,prism:doi", "count": "100", "sort": "relevancy"}
    data["start"] = start
    head = {"X-ELS-APIKey": key}
    x = requests.request("GET", citeurl, headers=head,params=data)
    data.pop("start")
    if x.status_code != 200:
        print(x.text)
        return False
    results = x.json()
    total = results["search-results"]["opensearch:totalResults"]
    print("total:", total)
    amount = int(total) if int(total) < amount else amount
    doilist = []
    while start < amount:
        print(start)
        data["cursor"] = results["search-results"]["cursor"]["@next"]
        for item in results["search-results"]["entry"]:
            try:
                doi = item["prism:doi"]
                doilist.append(doi)

            except:
                pass
        x = requests.request("GET", citeurl, headers=head,params=data)
        results = x.json()
        if x.status_code != 200:
            print(x.text)
            print("failed at: ", start)
            break
        start += 100
        print(len(list(dict.fromkeys(doilist))))
    return doilist

def getfigures(doi):
    key = "b6039e6ff3cd83f0fcd426ac57cfabe5"
    print(doi)
    contenturl = "https://api.elsevier.com/content/object/doi/" + doi
    head = {"X-ELS-APIKey": key}
    contentdata = {'apiKey': key, 'apiKey': key,}
    y = requests.request("GET", contenturl + doi, headers=head,params=contentdata)
    print(y.status_code)
    print(y.text)
    return True

# doi = r"10.2202/1542-6580.2238"
# getfigures(doi)
# # doi = "10.1016/j.apenergy.2019.114078
query = "TITLE-ABS-KEY(\"from syngas\" OR \"syngas to\" OR \"converting syngas\")"
doilist = search(query, 20000)
path = "C:\\Users\\Koen\\Documents\\Masterproject\\co hydrogenation\\fromsyngas\\"


for i,item in enumerate(doilist):
    print(i)
    getxml(item, path)



with open(path + "info.txt", "w+") as infofile:
    infofile.write(query)
    infofile.write("\n")
    infofile.write(path)


#bla
# doilist1 = []
# for item in doilist:
#     doi = getrefs(item)
#     if doi != False:
#         doilist1 += doi
# for item in doilist1[300:]:
#     if type(item) == type([]):
#         getxml(list(item[0].keys())[0])
#     else:
#         getxml(item)
#         time.sleep(0.1)
# for item in doilist:
#     if item:
#         getxml(item)
#         time.sleep(0.1)

#https://api.elsevier.com/content/search/scopus?query=DOI(10.1016/j.stem.2011.10.002)+OR+DOI(10.1098/rsbl.2011.0293)&field=citedby-count,prism:doi&apiKey=7f59af901d2d86f78a1fd60c1bf9426a
import requests
from pprint import pprint
import xml.etree.ElementTree as ET
from pathlib import Path


def getxml(doi, path):

    doiname = doi.replace(".", "").replace("\\", "").replace("/", "") + ".xml"
    filecheck = Path(path + doiname)
    try:
        if filecheck.is_file():
            print("Doi in list:", doiname)
            return False
    except:
        return False
    key = "1301c022331d8d916b328f10d475e9c1"
    url = 'https://api.elsevier.com/content/search/scopus'
    contenturl = "https://api.elsevier.com/content/article/doi/" + doi
    field = 'citedby-count,prism:doi'
    head = {"Accept": "text/xml"}
    data = {'apiKey': key,"view": "FULL", "xml-decode": "false"}

    r = requests.request("GET", contenturl, headers=head,params=data)
    if r.status_code == 200 and head["Accept"] == "text/xml":
        root = ET.fromstring(r.text)
        print(doi)
        with open(path + doiname, "wb") as outf:
            outf.write(r.text.encode("utf-8"))

    elif r.status_code == 200 and head["Accept"] == "text/plain":
        with open(r"\xmls\platinum.txt", "w+", encoding="utf-8") as txtfile:
            txtfile.write(r.text)

    elif r.status_code == 404:
        print("not found.")
    elif r.status_code == 400:
        print("code400")
    else:
        print(r.status_code)
        return False

    return True

# xml = getxml("doi:10.1016/S0014-5793(01)03313-0")
# xml = getxml("10.1016/S0920-5861(01)00477-1")
# type(xml)

import lxml.etree as etree
import re

def getxmlstring(xmlpath):
    with open(xmlpath, 'r',encoding='utf-8') as xmlfile:
        return xmlfile.read()


def gettitle(filename):
    if '.xml' in filename:
        xml = getxmlstring(filename)
        result = re.search('<dc:title>(.*?)<\/dc:title>', xml)

        if result:
            title = result.group(1)
            return title
        return None
    elif '.html' in filename:
        html = getxmlstring(filename)
        # print(html)
        result = re.search(r'<h1 id="sect\d*">(.*?)<\/h1>', html)
        # print('result------------')
        # print(result)
        # print('result------------')
        if result:
            title = result.group(1)
            title = re.sub("<.*?>", "", title)
            return title
        return None

def getabstract(filename):
    if '.xml' in filename:
        xml = getxmlstring(filename)

        result = re.search('<dc:description>(.*?)<\/dc:description>', xml, re.DOTALL)
        if result:
            abstract = result.group(1)
            return abstract
        return None
    elif '.html' in filename:
        html = getxmlstring(filename)
        result = re.search(r'<p class="abstract">(.*?)<\/p>', html)

        if result:

            abstract = result.group(1)
            abstract = re.sub("<.*?>", "", abstract)
            return abstract
        return None

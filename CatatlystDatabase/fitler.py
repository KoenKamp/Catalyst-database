
import os
import csv
import sys
from pprint import pprint
import json
import re
from gettitle import gettitle
import pickle
from random import shuffle
from gettitle import gettitle, getabstract
from jsontocsvghsv import jsonlisttocsv
from shutil import copyfile
# print 'Number of arguments:', len(sys.argv), 'arguments.'
# print 'Argument List:', str(sys.argv)

outpath = "wgs\jsonpost.csv"


path = r"C:\Users\Koen\Documents\Masterproject\RSC\wgs\\"
filteredpath = r"C:\Users\Koen\Documents\Masterproject\RSC\wgs\wgsfiltered2\\"
# with open ('importantpapers', 'rb') as fp:
#     importantfiles = pickle.load(fp)
for root, dirs, files in os.walk(path):
    # shuffle(files)
    # print(len(files))
    # print("suffled")
    for i,file in enumerate(files):
        # if file not in importantfiles:
        #     continue
        print("iteration:", i)
        print(path + file)
        filename = path + file
        abstract = getabstract(filename)
        title = gettitle(filename)
        # print(filename)
        # print(title)
        # print(abstract)
        print('abstract')
        print(abstract)
        print('title')
        print(title)
        # abstract = ""

        query = "(wgs)|(water.gas.shift)"

        # query = "(syngas to)|(from syngas)|(syngas conversion)|(co hydrogenation)|(hydrogenation of co(?!2))|(Fischer)"
        # query = "(co2 hydrogenation)|(hydrogenation of co2)"
        # name = "Biogas to methanol: A comparison of conversion processes involving direct carbon dioxide hydrogenation and via reverse water gas shift reaction"
        # print(re.search(query,name, flags=re.IGNORECASE))
        # quit()


        # print(re.search(query, title, flags=re.IGNORECASE))
        # print(re.search(query, abstract, flags=re.IGNORECASE))
        # print(notmatchtitle)
        # print(notmatchabstract)
        if title:
            notmatchtitle = re.search("(r.?wgs)|(reverse.?water.?gas.?shift)|(fischer)|(Co2 hydrogenation)", title, flags=re.IGNORECASE)
            searchtitle = re.search(query, title, flags=re.IGNORECASE)
        else:
            searchtitle = None
        if abstract:
            notmatchabstract = re.search("(r.?wgs)|(reverse.?water.?gas.?shift)|(fischer)|(Co2 hydrogenation)", abstract, flags=re.IGNORECASE)
            searchabstract = re.search(query, abstract, flags=re.IGNORECASE)
        else:
            searchabstract = None
        if searchtitle or searchabstract and not (notmatchtitle or notmatchabstract):
            # print("copied")
            copyfile(filename, filteredpath + file)

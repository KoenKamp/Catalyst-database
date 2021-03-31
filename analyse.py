from readxml import readxml
import os
import csv
import sys
from pprint import pprint
import json
import re
from gettitle import gettitle, getabstract
import pickle
from random import shuffle

from jsontocsvghsv import jsonlisttocsv



# print 'Number of arguments:', len(sys.argv), 'arguments.'
# print 'Argument List:', str(sys.argv)
if len(sys.argv) > 1:
    outpath = sys.argv[1] + ".csv"
else:
    outpath = r"co hydrogenation\oof.csv"
if len(sys.argv) > 2:
    if sys.argv[2] == 'replace':
        with open(outpath, "w+"):
            pass
    if sys.argv[2] == 'test':
        testset = True
    else:
        testset = False
else:
    testset = False
try:
    f = open(outpath)
    writeheader = False
    # Do something with the file
except IOError:
    writeheader = True

#  CO2
allxml = r"C:\Users\Koen\Documents\Masterproject\CO2 hydrogenation\allxml\\"
allhtml = r"C:\Users\Koen\Documents\Masterproject\RSC\co2 hydrogenation\all html filtered\\"

# # CO
allxml = r"C:\Users\Koen\Documents\Masterproject\CO hydrogenation\All xml\\"
allhtml = r"C:\Users\Koen\Documents\Masterproject\RSC\co hydrogenation\CO all html\\"

#wgsf
# allxml = r"C:\Users\Koen\Documents\Masterproject\WGS\filteredlast\\"
# allhtml = r"C:\Users\Koen\Documents\Masterproject\RSC\wgs\wgsfiltered2\\"


pathlist = [allxml, allhtml]
chemnames =["H","He","Li","Be","B","C","N","O","F","Ne","Na","Mg","Al","Si","P","S","Cl","Ar","K","Ca","Sc","Ti","V","Cr","Mn","Fe","Co","Ni","Cu","Zn","Ga","Ge","As","Se","Br","Kr","Rb","Sr","Y","Zr","Nb","Mo","Tc","Ru","Rh","Pd","Ag","Cd","In","Sn","Sb","Te","I","Xe","Cs","Ba","La","Ce","Pr","Nd","Pm","Sm","Eu","Gd","Tb","Dy","Ho","Er","Tm","Yb","Lu","Hf","Ta","W","Re","Os","Ir","Pt","Au","Hg","Tl","Pb","Bi","Po","At","Rn","Fr","Ra","Ac","Th","Pa","U","Np","Pu","Am","Cm","Bk","Cf","Es","Fm","Md","No","Lr","Rf","Db","Sg","Bh","Hs","Mt","Ds","Rg","Cn","Nh","Fl","Mc","Lv","Ts","Og"]
results = []
# with open ('importantpapers', 'rb') as fp:
#     importantfiles = pickle.load(fp)
for path in pathlist:
    for root, dirs, files in os.walk(path):
        shuffle(files)
        print(len(files))
        print("suffled")
        for i,file in enumerate(files):
            if "xml" not in file and 'html' not in file:
                continue
            if "json" in file:
                continue
            print("iteration:", i)
            print(path + file)

            result = readxml(path + file)
            pprint(result)
            if not result:
                print("file can't be read")
                continue



            # with open(path.replace(r"\files\\", "").replace(r"\filteredfiles\\", "").replace(r"\htmlfiles\\", '').replace(r"\test\\", "") + r"\jsons\\" + file.replace(".xml", "").replace('.html', "") + ".json", "w+") as jsonout:
            #     json.dump(result, jsonout)
            rows = jsonlisttocsv(result)
            print(rows)
            if testset == True and len(rows) != 0:
                end = False
                while end == False:
                    word = input('Save?')
                    print()

                    if 'y' in word:
                        rows.to_csv(r"wgs/checks//" + file.strip(".xml") + ".sav")
                        end = True
                    elif 'n' in word:
                        end = True
            if len(rows) > 0:
                rows.to_csv(outpath, mode='a', header=writeheader)
                writeheader=False

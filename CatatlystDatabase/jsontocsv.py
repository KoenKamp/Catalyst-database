import json
import csv
import matplotlib.pyplot as plt
import re
import numpy as np
import pandas as pd
from pprint import pprint
import pickle
from mpl_toolkits.mplot3d import Axes3D

def supportextract(name):
    supports = ["ceria", "alumina", "silica", "SBA", "ZSM", "CNT", "Al2O3", "MgO", "CeO2", "TiO2", "CMK", "MnO", "Y2O3", "ZrO2","Tb4O7", "HfO2", "La2O3", "Co3O4","ThO2", "SiO2", "Fe2O3", "Sm2O3", "Mo2C", "Gd2O3", "Yb2O3","CaO", "CuO", "NiO"]
    support = ""
    if name:
        for j, supp in enumerate(supports):
            cleanedsupp = ''.join([i for i in supp if not i.isdigit()])
            cleanedname = ''.join([i for i in name if not i.isdigit()])
            if cleanedsupp in cleanedname:
                support += supp
        if support != "":
            rowdict["support"] = support
        else:
            support = None
        return support
    else:
        return None

def elementextract(name):
    """
    inputs a string and extracts relevant elements
    """
    support =  ""
    activephase = ["Sc", "Ti", "V	Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Y", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "La", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg", "Ac", "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds", "Rg"]

    if name:
        #active phase detection
        elements = ""
        for j, element in enumerate(activephase):
            if element in name:
                elements += element
        if elements != "":
            rowdict['elements'] = elements
        else:
            elements = False
        return elements
    else:
        return False

def jsonlisttocsv(json):
    convcounter = 0
    # activephase = ["Co", "Ni","Cu", "Ru", "Rh", "Pd", "Pt", "Au", "Fe", "Mo"]
    activephase = ["Sc", "Ti", "V	Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Y", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "La", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg", "Ac", "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds", "Rg"]
    supports = ["SBA", "ZSM", "CNT", "Al2O3", "MgO", "CeO2", "TiO2", "CMK", "MnO", "Y2O3", "ZrO2","Tb4O7", "HfO2", "La2O3", "Co3O4","ThO2", "SiO2", "Fe2O3", "Sm2O3", "Mo2C", "Gd2O3", "Yb2O3","CaO", "CuO", "NiO"]

    usedpapers = []
    m = 0
    data = pd.DataFrame(columns=["elements","temp","conv"])
    for file in json:
        filename = file["title"]

        # find the composition in the text, and find the temperature unit used

        txtcomp= ""
        tempunits = ""
        captionname = False
        captioncomp = None
        captionflow = None
        for result in file['results']:
            keys = result.keys()
            if "txtcomp" in keys:
                for value in result["txtcomp"]:
                    for element in value["values"]:
                        if "CO" in element or "H2O" in element or "H2" in element:
                            txtcomp += element


            if "conv" in result.keys():
                for item in result["conv"]:
                    if "tempunits" in item.keys():
                        tempunits = item["tempunits"]
                    if "comp" in item.keys():
                        captioncomp = item["comp"]
                    if "flow" in item.keys():
                        captionflow = item["flow"] + item["flowunit"]
        if tempunits == "":
            for result in file["results"]:
                if "temp" in result.keys():
                    if "unit" in result["temp"][0].keys():
                        tempunits = result["temp"][0]["unit"].strip("[]")
                        break
        oldname = None

        for result in file['results']:
            keys = result.keys()

            # catalyst name translator
            name = ""
            backupname = ""
            usecaption = True
            captionname = False
            if 'catalyst_name' in keys:
                for catalyst in result['catalyst_name']:
                    name += catalyst["name"]
                usecaption=False
            elif "names" in keys:
                for catalyst in result['names']:
                    backupname += catalyst
            elif oldname:
                name = oldname
            else:
                name = None
            if name:
                oldname = name
            # flowrate or equivilent translator
            flow = ""
            if 'flow' in keys:
                for flowcondition in result['flow']:
                    flow += flowcondition["value"]

            #composition translator
            comp = ""
            if 'comp' in keys:
                for composition in result['comp']:
                    for element in composition["values"]:
                        comp += element


            # temperature translator
            temp = ""
            if 'temp' in keys:
                for temperature in result['temp']:
                    if "value" in temperature.keys():
                        temp += temperature["value"] + tempunits

            # conversion/temp json translator/cleaner
            conv = []
            if 'conv' in keys:
                for i,conversion in enumerate(result['conv']):
                    convstring = None
                    tempstring = None
                    if "convunits" in conversion.keys() and "convvalue" in conversion.keys():
                        if conversion["convunits"] != "Equilibrium":
                            convstring = conversion["convvalue"] + conversion["convunits"]
                    elif "convvalue" in conversion.keys():
                        convstring = conversion["convvalue"]
                    if "captioncatname" in conversion.keys():
                        captionname = conversion["captioncatname"]
                    if "tofvalue" in conversion.keys():
                        tofstring = conversion["tofvalue"]
                    else:
                        tofstring = None
                    if "tempvalue" in conversion.keys():
                        tempstring = conversion["tempvalue"] +  tempunits
                    if "check" in conversion.keys() and conversion["check"] == "True":
                        if "captioninfo" in conversion.keys() and conversion["captioninfo"] == "conversion":
                            pass
                        else:
                            convstring = None

                    if convstring or tofstring:
                        if temp:
                            conv.append([convstring, temp, tofstring])
                        elif tempstring:
                            conv.append([convstring,tempstring, tofstring])
                # if comp == "":
            #     comp = txtcomp

            # convert temperature string to numerical

            floats = []
            for convstring, tempstring, tofstring in conv:
                #temperature
                if (u"°C") in tempstring:
                    tempfloat = re.sub("[^0-9]", "", tempstring)
                    tempfloat = float(tempfloat) + 273.15
                elif (u"K") in tempstring:
                    tempfloat = re.sub("[^0-9]", "", tempstring)
                    tempfloat = float(tempfloat)
                else:
                    convcounter += 1
                    tempfloat = None

                if convstring:
                    #conversion
                    convfloat = re.sub("[^0-9.,/]", "", convstring)
                    if convfloat != "." and convfloat != "," and convfloat != "":
                        try:
                            if "," in convfloat:
                                convfloat = float(convfloat.replace(",","."))
                            else:
                                convfloat = float(convfloat)
                        except ValueError:
                            print(convfloat)
                            convfloat = None
                    else:
                        convfloat = None
                if (convfloat or tofstring) and tempfloat:
                    floats.append([convfloat, tempfloat, tofstring])

            # if conv:
            #     print(conv)
            #     print(convfloats)

            rowdict = {}
            if comp:
                rowdict["comp"] = comp
            elif captioncomp != "[]" and captioncomp != None:
                rowdict["comp"] = captioncomp
            elif txtcomp != "":
                rowdict["comp"] = txtcomp

            if flow != "":
                flowfloat = re.sub("[^0-9.]", "", flow)
                if flowfloat != "":
                    try:
                        flowfloat = float(flowfloat)
                        if flowfloat < 12000 and flowfloat > 0.5:
                            rowdict["flow"] = flowfloat
                    except:
                        pass

            elif captionflow:
                flow = captionflow
                flowfloat = re.sub("[^0-9.]", "", flow)
                if flowfloat != "":
                    try:
                        flowfloat = float(flowfloat)
                        if flowfloat < 12000 and flowfloat > 0.5:
                            rowdict["flow"] = flowfloat
                    except:
                        pass
            rowdict["filename"] = filename
            # name

            elements = elementextract(name)
            support = supportextract(name)
            if not elements:
                elements = elementextract(captionname)
                if not elements:
                    elements = elementextract(backupname)
            if not support:
                support = supportextract(captionname)
                if not support:
                    support = supportextract(backupname)

            if len(floats) != 0:
                for k, conv in enumerate(floats):
                    # if floats[k][1] < 1200 and floats[k][1] > 0:
                    #     if floats[k][0] > 0 and floats[k][0] < 100:
                            rowdict['temp'] = floats[k][1]
                            rowdict['conv'] = floats[k][0]
                            rowdict["tof"] = floats[k][2]
                            data = data.append(rowdict,ignore_index=True)
    return data
# usedpapers = list(dict.fromkeys(usedpapers))
# with open('importantpapers', 'wb') as fp:
#     pickle.dump(usedpapers, fp)

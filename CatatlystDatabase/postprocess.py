import json
import csv
import matplotlib.pyplot as plt
import matplotlib as mpl
import re
import numpy as np
import pandas as pd
from pprint import pprint
import pickle
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pylab as pylab

colors = ['tab:orange', 'tab:red', 'tab:pink', 'tab:brown', 'tab:purple','tab:blue']

#Co2 hydrogenation
names = ["Co", "Fe", "Ni", "Pd", "Ru", "Cu"]
#wgs
names = ["Co", "Fe", "Ca", "Pd", "Pt","Cu"]
colors = ['tab:purple']
names = ['Pt']
# #Co hydro
names = ["Cu" , "Mn", "Pd", "Pt","Fe","Co"]
colors = ['tab:blue', 'tab:pink', 'tab:brown', 'tab:purple','tab:red','tab:orange']


params = {'legend.fontsize': 'x-large',
          'figure.figsize': (9, 7),
         'axes.labelsize': 'x-large',
         'axes.titlesize':'x-large',
         'xtick.labelsize':'x-large',
         'ytick.labelsize':'x-large',
         'figure.subplot.bottom': 0.080,
          'figure.subplot.hspace': 0.2,
          'figure.subplot.left': 0.104,
          'figure.subplot.right': 0.974,
          'figure.subplot.top': 0.947,
          'figure.subplot.wspace': 0.2,}
pylab.rcParams.update(params)

activephase = ["K", "Mg", "Na", "Al", "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "La", "Hf", "Ta", "Re", "Os", "Ir", "Pt", "Au", "Hg", "Ac", "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds", "Rg"]
supports = ["ZnO", "YSZ", "ceria", "alumina", "silica", "SBA", "ZSM", "CNT", "Al2O3", "MgO", "CeO2", "TiO2", "CMK", "MnO", "Y2O3", "ZrO2","Tb4O7", "HfO2", "La2O3", "Co3O4","ThO2", "SiO2", "Fe2O3", "Sm2O3", "Mo2C", "Gd2O3", "Yb2O3","CaO", "CuO", "NiO"]
def onpick3(event):
    ind = event.ind
    print('onpick3 scatter:', ind, np.take(labels, ind))

def cleanduplicates(name, elements):
    # print('ran')
    for element in elements:
        matches = re.findall(element + "(?!\d?O)", name)
        count = len(matches)
        if  count > 1:
            # print(name)
            # print(name.replace(support,"") + support)
            name = re.sub(element + "(?!\d?O)", "", name) + element
            # print(name)
    return name

def cleanelements(name, element=None):
    if element == None:
        return None
    elif type(name) == type(""):
        replacedname = name.replace(element, "")
        if replacedname == "":
            # print(name)
            return cleanduplicates(name, activephase)
        else:
            return cleanduplicates(replacedname, activephase)

    else:
        return None

def cleansupport(name, support=None):
    if type(name) == type(""):
        name = name.replace("silica", "SiO2").replace("alumina", "Al2O3").replace("ceria", "CeO2")
        count = name.count(support)
        if  count > 1:
            # print(name.replace(support,"") + support)
            return  name.replace(support,"") + support
        else:
            return name
    else:
        return None

def cleanunit(name):
    if type(name) == type(""):
        name = name.replace("selectivity", "").strip("S").replace("(%)", "").replace("%", "")
        if 'yield' in name:
            return None
        if name == "CH3OH":
            return "MeOH"
    return name

def cleancomp(x):
    if type(x) == type(1):
        return x
    elif type(x) == type(''):
        if "|" not in x:
            x = x.replace('\'', "\"").replace("\"\"", "\"")
            # print(x)
            try:
                x = json.loads(x)
            except:
                return None
            if type(x) == type([]):
                try:
                    return float(x[0])
                except:
                    return None
            if 'CO' in x.keys() and 'H2' in x.keys():
                # print(x['CO'])
                # print(x['H2'])
                if float(x['CO']) != 0:
                    return   float(x['H2']) / float(x['CO'])
            elif 'carbonmonoxide' in x.keys() and 'hydrogen' in x.keys():
                return   float(x['hydrogen']) / float(x['carbonmonoxide'])
            for key in x.keys():
                if 'H2' in key and 'CO' in key:
                    h2 = key.find('H2')
                    co = key.find('CO')

                    if h2 > co:
                        return float(re.sub("[^0-9\.]", "", x[key]))
                    else:
                        return 1/float(re.sub("[^0-9\.]", "", x[key]))

        else:
            x.split("|")
            return float(x[0])

def printstats(data):
    print("all:", len(data.dropna()))
    print(data)
    # data.drop(['support'], inplace=True,axis=1)
    print(data)
    print("Count: ")
    print(data.count())

    test = data[data['conv'].notna()]
    print("temp missing: ", test["temp"].isna().sum())
    print("name missing: ", test["elements"].isna().sum())
    # print("support missing: ", test["support"].isna().sum())
    print("comp missing: ", test["comp"].isna().sum())
    print("flow missing: ", test["flow"].isna().sum())
    # print("selectivity missing: ", test["selectivity"].isna().sum())
    # print("presssure missing: ", test["pressure"].isna().sum())

    print("all:", len(data.dropna()))

def elementsbar(data):
    testdata = data['elements'] + data['support']
    # print(testdata.value_counts()[:10])
    testdata.value_counts()[:10].plot.bar(rot=0)
    plt.title("10 most commonly used catalyst compositions in CO hydrogenation")
    plt.xlabel("Elements")
    plt.ylabel("Number of occurances")
    plt.show()

def supportbar(data):
    data["support"].value_counts()[:10].plot.bar(rot=0)
    plt.xlabel("Name")
    plt.ylabel("occurances")
    plt.title("10 most commonly used oxides in the water-gas shift reaction")
    plt.show()

def temphist(data):
    data['temp'].hist(bins=30, range=(450,700))
    plt.title("Histogram of all temperatures found for CO hydrogenation")
    plt.xlabel("Temperature (K)")
    plt.ylabel("occurances")
    plt.show()

def unitbar(data):
    data["unit"].value_counts()[:10].plot.bar(rot=0)
    plt.title("10 most common products found in CO2 hydrogenation")
    plt.ylabel("occurances")
    plt.xlabel("Product name")
    plt.show()

def pressureunitbar(data):
    data["pressureunit"].value_counts()[:10].plot.bar(rot=0)
    # data = data[data.pressureunit.str.contains("bar",na=False,flags=re.IGNORECASE)]
    plt.title("10 most common products found in CO2 hydrogenation")
    plt.ylabel("occurances")
    plt.show()

def pressurehist(data):
    data.loc[data.pressureunit.str.contains("bar",na=False,flags=re.IGNORECASE), ['pressure']].hist(bins=20, range=(0,101))
    plt.title("Histogram of pressures found for the CO2 hydrogenation reaction")
    plt.xlabel("Pressure (bar)")
    plt.ylabel("occurances")
    plt.show()

def comphist(data):
    plt.hist(list(data['comp'].dropna()), range=(0,4), bins=30)
    # data['comp'].hist(bins=20, range=(0,101))
    plt.title("Histogram of all H2/CO  ratios found for CO hydrogenation")
    plt.xlabel("Ratio (H2/CO)")
    plt.ylabel("occurances")
    plt.show()


def pressureselectivity(data):
    occurances = data["elements"].value_counts() > 10
    occurances = occurances[occurances == True][:10]
    names = occurances.index.values.tolist()
    fig, ax = plt.subplots()
    for i, element in enumerate(names):
        if element == "":
            label = "-"
        else:
            label = element

        elementdata = data.loc[data["elements"].str.contains(element,na=False)]
        elementdata = elementdata.loc[elementdata["unit"].str.contains("C5+",na=False,flags=re.IGNORECASE)]
        elementdata.plot("pressure", "selectivity", 'scatter', label=label, c=colors[i], ax=ax)

        plt.xlim(0,100)

    plt.title("CO2 hydrogenation C5+ selectivity over pressure")
    plt.xlabel("pressure (bar)")
    plt.ylabel('selectivity %')
    plt.show()

def tempconv(data, labels=None):
    fig, ax = plt.subplots()

    for i, element in enumerate(names):

        elementdata = data.loc[data["elements"].str.contains(element,na=False)]
        if element == 'Cu':
            marker = '^'
        elif element == 'Fe':
            marker = 'x'
        elif element == 'Ni':
            marker = 'P'
        elif element == "Co":
            marker = 'D'
        else:
            marker = '.'
        # print(marker)
        # temp = np.linspace(400,700)
        # plt.plot(temp, np.exp((4577.8/temp) - 4.33))
        elementdata = elementdata[elementdata['temp'] < 1200]
        average = elementdata.dropna(subset=['elements', 'temp','conv'])['temp'].mean()
        print(element)
        print(average)
        # plt.vlines(573, 0, 100, color='black')
        plot = elementdata.plot("temp", "conv", 'scatter', label=element, c=colors[i], ax=ax, picker=True, linewidths=1, marker='o', alpha=0.8)
        labeldata = elementdata[['temp', 'conv', 'filename']].copy()
        labeldata = labeldata.dropna()
        labels += labeldata['filename'].tolist()
        # plt.hlines(average, 0,100,colors=colors[i])
        plt.xlim(400,1000)
        plt.ylim(0,100)

    fig.canvas.mpl_connect('pick_event', onpick3)
    leg = plt.legend()
    for lh in leg.legendHandles:
        lh.set_alpha(1)
    plt.title("Water gas shift temperature over conversion using platnium")
    plt.xlabel("Temp (K)")
    plt.ylabel("conv (%)")
    plt.show()


def tempconvselec(data, unit, ax=None):
# Plot for the colormapped selectivity
    colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']
    if unit == "CH4":
        searchunit = "Ch4|methane|c1"
    elif unit == "MeOH":
        searchunit = "MeOH|CH3OH|methanol"
    elif unit == "C2+":
        searchunit = "C2|C3|c4|c5|c6|C7|c8|c9|c10|c11|c12"
    else:
        searchunit = unit
    labels = []
    fig, ax = plt.subplots()
    elementdata = data.loc[data["unit"].str.contains(searchunit,na=False, flags=re.IGNORECASE)]
    elementdata.plot("temp", "conv", 'scatter', c=elementdata['selectivity'],cmap='plasma', vmin=0, vmax=100)
    # labeldata = elementdata[['temp', 'conv', 'filename']].copy()
    # labeldata = labeldata.dropna()
    # labels += labeldata['filename'].tolist()
    # print(labels)

    # fig.canvas.mpl_connect('pick_event', onpick3)
    # fig = plt.gcf()
    # cax = fig.get_axes()[1]
    # #and we can modify it, i.e.:
    # cax.set_ylabel('Selectivity towards ' + unit)
    plt.xlim(400,1000)
    plt.ylim(0,100)
    plt.title("CO2 hydrogenation color coded by selectivity towards " + unit)
    plt.xlabel("Temp (K)")
    plt.ylabel("conv (%)")
    plt.legend()

    # if ax = None:
    plt.show()


def presselec(data,unit):
    # selectivity with pressures
    if unit == "CH4":
        searchunit = "Ch4|methane|c1"
    elif unit == "MeOH":
        searchunit = "MeOH|CH3OH|methanol"
    elif unit == "C2+":
        searchunit = "C2|C3|c4|c5|c6"
    else:
        searchunit = unit


    # colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']
    fig, ax = plt.subplots()
    for i, element in enumerate(names):
        print(len(data["elements"].str.contains(element,na=False)))
        elementdata = data[data["elements"].str.contains(element,na=False)]
        elementdata = elementdata[elementdata["unit"].str.contains(unit,na=False,flags=re.IGNORECASE)]
        if element == 'Co':
            marker = '^'
        elif element == 'Fe':
            marker = 'x'
        else:
            marker = '.'
        elementdata.plot("pressure", "selectivity", 'scatter', c=colors[i],label=element,ax=ax,cmap='viridis', marker=marker,linewidths=1)
        # fig = plt.gcf()
        # cax = fig.get_axes()[1]
        # #and we can modify it, i.e.:
        # cax.set_ylabel('Selectivity towards methane')
        plt.xlim(0,100)
        plt.ylim(0,100)
        plt.title("CO hydrogenation selectivity towards "+unit+" color coded by element")
        plt.xlabel("Pressure (bar)")
        plt.ylabel("Selectivity (%)")
        plt.legend()
    plt.show()

def selechigherthan(data):
    colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']

    # names = ["Al", "Si", "Zr"]
    fig, ax = plt.subplots()
    for i, element in enumerate(names):
        if element == "":
            label = "-"
        else:
            label = element
        elementdata = data[data["elements"].str.contains(element,na=False, flags=re.IGNORECASE)]
        # elementdata = elementdata[elementdata['selectivity'] > 50]
        elementdata = elementdata.loc[elementdata["unit"].str.contains("CH4|methane",na=False,flags=re.IGNORECASE)]
        elementdata.plot("temp", "conv", 'scatter', label=label, c=colors[i], ax=ax)
        # plt.figure(21)
        # elementdata.groupby("support")['selectivity'].agg(['size', 'mean']).sort_values(by='size', ascending=False)[:10].plot.bar(rot=0)
        # plt.title(element + "based catalyst average prerformance with each support")
        # plt.legend(["Sample size", "Selectaivity mean"])
        # plt.show()
    plt.xlim(400,1000)
    plt.ylim(0,100)
    plt.title("Temperature plotted over conversion color coded by element for CO2 hydrogenation with >70% CO selectivity")
    plt.xlabel("Temp (K)")
    plt.ylabel("conv (%)")
    plt.legend()
    plt.show()

def tempconv2(data):
    colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']

    for i, element in enumerate(names):
        if element == "":
            label = "-"
        else:
            label = element
        # plt.hlines(y, xmin, xmax, colors='k', linestyles='solid', label='', *, data=None, **kwargs)[source]
        elementdata = data.loc[data["elements"].str.contains(element,na=False, flags=re.IGNORECASE)]
        average = data.loc[data['elements'] == element]['temp'].mean()
        print("element: ", element)
        print("average: ", average)
        print()

        # counts = elementdata["support"].value_counts()
        # print(counts)
        # elementdata.loc[elementdata['support'] == counts.index[0]].plot("conv", "temp", 'scatter', label=counts.index[0], c=colors[0], ax=ax)
        # elementdata.loc[elementdata['support'] == counts.index[1]].plot("conv", "temp", 'scatter', label=counts.index[1], c=colors[1], ax=ax)
        # elementdata.loc[elementdata['support'] == counts.index[2]].plot("conv", "temp", 'scatter', label=counts.index[2], c=colors[2], ax=ax)
        # elementdata.loc[elementdata['support'] == counts.index[3]].plot("conv", "temp", 'scatter', label=counts.index[3], c=colors[3], ax=ax)
        elementdata.plot("temp", "conv", 'scatter', label=label, c=colors[i], ax=ax)
        plt.hlines(average, 0,100,colors=colors[i])
        plt.xlim(400,1000)
        plt.ylim(0,100)

        plt.figure(20)
    plt.title("CO2 hydrogenation temperature over conversion by element")
    plt.xlabel("Temp (K)")
    plt.ylabel("conv (%)")
    plt.show()



def flowunit(data):
    data["flowunit"].value_counts()[:10].plot.bar(rot=0)
    plt.title("CO hydrogenation flowrate unit occurances")
    plt.xlabel("Parsed unit")
    plt.ylabel("Occurances")
    plt.show()

def flowtempconv(data):
    filteredflow = data[data["flowunit"].str.contains('^h',na=False)]
    filteredflow = filteredflow[filteredflow['temp'] < 1500]
    filteredflow = filteredflow[filteredflow['flow'] < 20000]
    fig = plt.figure(figsize=(12, 9))
    ax = Axes3D(fig)

    # names = occurances.index.values.tolist()

    for i, element in enumerate(names):
        # plt.hlines(y, xmin, xmax, colors='k', linestyles='solid', label='', *, data=None, **kwargs)[source]
        test = filteredflow[filteredflow["elements"].str.contains(element,na=False)]
        y = test["temp"]

        x = test["flow"]
        # print(x[x.notna()])
        z = test["conv"]
        ax.scatter(x,y,z, label=element,color=colors[i])  # this way you can control color/marker/size of each group freely
        # ax.scatter(*df.iloc[grp_idx, [0, 1, 2]].T.values, label=grp_name)  # if you want to do everything in one line, lol
    plt.legend()
    plt.title("with temp/conv combination flow?")
    ax.set_xlabel('flow (GHSV, h-1)')
    ax.set_ylabel('temp (K)')
    ax.set_zlabel(r'conv (%)')
    plt.show()

def plotflowunit(data):
    data["flowunit"].value_counts()[:20].plot.bar(rot=0)
    plt.show()

data = pd.read_csv(r"wgs/GHSVtest.csv", index_col=0)
data.drop_duplicates(inplace=True)
data.drop(['bet'], axis=1,inplace=True)
data[['flow','flowunit']] = data.flow.str.split("|",expand=True)
data["flow"] = pd.to_numeric(data['flow'],errors='coerce')

data[['pressure', 'pressureunit']] = data.pressure.str.split("|", expand=True)
data["pressure"] = pd.to_numeric(data['pressure'],errors='coerce')
print("----" * 10)
data.loc[data.pressureunit.str.contains("MPa",na=False,flags=re.IGNORECASE), ['pressure']] *= 10
data.loc[data.pressureunit.str.contains("kPa",na=False,flags=re.IGNORECASE), ['pressure']] /= 100
data.loc[data.pressureunit.str.contains("MP",na=False,flags=re.IGNORECASE), ['pressureunit']] = 'bar'
data.loc[data.pressureunit.str.contains("kPa",na=False,flags=re.IGNORECASE), ['pressureunit']] = 'bar'
data.loc[data.pressureunit.str.contains("atm",na=False,flags=re.IGNORECASE), ['pressure']] *= 1.01325
data.loc[data.pressureunit.str.contains("atm",na=False,flags=re.IGNORECASE), ['pressureunit']] = 'bar'
data.loc[data.pressureunit.str.contains("hpa",na=False,flags=re.IGNORECASE), ['pressure']] /= 1000
data.loc[data.pressureunit.str.contains("hpa",na=False,flags=re.IGNORECASE), ['pressureunit']] = 'bar'
data[['selectivity','unit']] = data.selectivity.str.split("|",expand=True,)
data['unit'] = data['unit'].apply(cleanunit)
data['comp'] = data['comp'].apply(cleancomp)
data["selectivity"] = pd.to_numeric(data['selectivity'],errors='coerce')
# data = data[data['selectivity'] < 100]

data["yield"] = data["selectivity"] / 100 * data["conv"] / 100

# data.drop(['support'], axis=1, inplace=True)
for support in supports:
    # print(support)
    # print(data.loc[data.elements.str.contains(support,na=False,flags=re.IGNORECASE), 'support'])
    data.loc[data.elements.str.contains(support,na=False,flags=re.IGNORECASE), 'support'] += support
    # print(data.loc[data.elements.str.contains(support,na=False,flags=re.IGNORECASE), 'support'])
    data['elements'] = data['elements'].apply(cleanelements, element=support)
for support in supports:
    data['support'] = data['support'].apply(cleansupport, support=support)
# data = data[~data['conv'].duplicated(keep=False) | data[['selectivity']].notnull().any(axis=1)]
# data.drop(["pressure", 'selectivity', 'unit', 'yield', 'pressureunit'], axis=1, inplace=True)
# data['elements'] = data['support'] + data['elements']

labels=[]
# printstats(data)
# df = data.dropna(subset=['selectivity'])
# data = data.drop(df.index)
printstats(data)
elementsbar(data)
# supportbar(data)
# temphist(data)
# pressurehist(data)
# comphist(data)
# flowunit(data)
# printstats(data)
tempconv(data, labels=labels)
# unitbar(data)
# data = data[data['selectivity'] < 100]
# tempconvselec(data, "MeOH")
# tempconvselec(data, "CH4")
# tempconvselec(data, "CO2")
# tempconvselec(data, "C2+")
# tempconv(data, labels=labels)
# unitbar(data)
plotflowunit(data)
# tempconv(data)
temphist(data)
presselec(data, "MeOH")
presselec(data, "CH4")
presselec(data, "CO2")
presselec(data, "C2+")

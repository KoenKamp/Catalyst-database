from chemdataextractor import Document
import chemdataextractor
from chemdataextractor.reader import XmlReader, ElsevierXmlReader
from lxml.etree import XMLParser
import lxml.etree as etree
import matplotlib.pyplot as plt
import re
from chemdataextractor.parse import R, I, W, Optional, merge, ZeroOrMore, OneOrMore
from chemdataextractor.model import BaseModel, StringType, ListType, ModelType

from chemdataextractor import Document
from chemdataextractor.model import Compound
from chemdataextractor.doc import Paragraph, Heading, Sentence
from chemdataextractor.parse import R, I, W, Optional, merge, T, SkipTo, Any, Group
from chemdataextractor.parse.base import BaseParser
from chemdataextractor.utils import first
from chemdataextractor.parse.base import BaseParser
from chemdataextractor.utils import first
from pprint import pprint
from tableParsers import *

def find_subset(items, target, acc=[]):
  if target == 0:
    return acc
  if len(items) == 0:
    return None
  acc_take = acc.copy()
  acc_take.append(items[0])
  take = find_subset(items[1:], target - items[0], acc_take)
  if take:
    return take
  return find_subset(items[1:], target, acc)


units = (Optional("(") + Optional(R(u'°')) + R(u'[CFK℃]')).add_action(merge)(u'units')
value = (Optional(R('~')) + R(u'^\d{3,4}')).add_action(merge)(u'value')
value2 = (Optional(R('~')) + R(u'^\d{3,4}(°C|K)')).add_action(merge)(u'value')
temp1 = (value+ units)(u'temp1')
temp2 = value2
temp = (temp1 | value2)(u'tempphrase')
#for catalyst name
supportstring = "ZnO|YSZ|ceria|alumina|silica|SBA|ZSM|CNT|Al2O3|MgO|CeO2|TiO2|CMK|MnO|Y2O3|ZrO2|Tb4O7|HfO2|La2O3|Co3O4|ThO2|SiO2|Fe2O3|Sm2O3|Mo2C|Gd2O3|Yb2O3|CaO|CuO|NiO"
symbolstring = "|Li|Be|Ne|Na|Mg|Al|Si|Cl|Ox|Ca|Sc|Ti|V|Cr|Mn|Fe|Co|Ni|Cu|Zn|Ga|Ge|As|Se|Br|Kr|Rb|Sr|Y|Zr|Nb|Mo|Tc|Ru|Rh|Pd|Ag|Cd|In|Sn|Sb|Te|Xe|Cs|Ba|La|Ce|Pr|Nd|Pm|Sm|Eu|Gd|Tb|Dy|Ho|Er|Tm|Yb|Lu|Hf|Ta|Re|Os|Ir|Pt|Au|Hg|Tl|Pb|Bi|Po|At|Rn|Fr|Ra|Ac|Th|Pa|Np|Pu|Am|Cm|Bk|Cf|Es|Fm|Md|No|Lr|Rf|Db|Sg|Bh|Hs|Mt|Ds|Rg|Cn|Nh|Fl|Mc|Lv|Ts|Og"
name = (R(u"^(("+symbolstring+"|" + supportstring + ")(?![a-z])(([A-Zα-ωΑ-Ω0-9\/\-,\.]|(wt.?))[a-zA-Z0-9α-ωΑ-Ω0-9\/\-,\.]*)?)"))
post = R("^([A-Z]|[0-9]|(wt.?)|"+symbolstring+u"|\/|-|\.|,|%|\(|\))+$") | T("SYM")
name = (name + ZeroOrMore(post))(u"name").add_action(merge)
prefix = R("^(Catalysts?)|(precursors?)|(abb)|(sample)|(abb)|(materials?)|(support)|(activity)|(catalytic)$", re.IGNORECASE)(u"prefix")


precat = (prefix + SkipTo(name) + name)("precat")
catpre = (name + SkipTo(prefix) + prefix)("catpre")
cat = (precat | catpre)(u"cat_phrase")

caption_context = cat

# caption_context = OneOrMore(Any())(u"test")
class FootTempParser(BaseParser):
    """"""
    root = temp

    def __init__(self):
        pass

    def interpret(self, result, start, end):
        context = {}
        # print("footnote temp")
        # print(etree.tostring(result))
        # print()
        c = Compound()

        context = {}
        tempvalue = first(result.xpath('//value/text()'))
        tempunit = first(result.xpath('//units/text()'))
        if tempunit and '℃' in tempunit:
            tempunit = '°C'
        if not tempvalue and not tempunit:
            tempvalue = first(result.xpath('//tempphrase/text()'))
            # print(tempvalue)
        if not tempunit:
            if "K" in tempvalue:
                tempunit = 'K'
                tempvalue = tempvalue.strip('K')
            elif '°C' in tempvalue:
                tempunit = '°C'
                tempvalue = tempvalue.strip("°C")
            else:
                tempvalue = None

        context["tempvalue"] = tempvalue
        context["tempunits"] = tempunit
        if context:
            c.conv.append(Conv(**context))
        yield c


class FootCatParser(BaseParser):
    """"""
    root = caption_context

    def __init__(self):
        pass

    def interpret(self, result, start, end):
        context = {}
        # print("footnote")
        # print(etree.tostring(result))
        # print()
        c = Compound()
        catname = first(result.xpath('./cat_phrase/name/text()'))
        # print(catname)
        context["captioncatname"] = catname
        if context:
            c.conv.append(Conv(**context))
        yield c

flowunit = R(r"^((h(-|−)1|ml|s|cm3|min|gcat|cat(alyst)?|l)(-|−)?\d*)$", re.IGNORECASE)
flowunitpre = R(r"×|\\|\/|:|\(|\)|<|>|[|]|\.|-|−", re.IGNORECASE)
flowunitafter = R(r"^(h|ml|s|m|g|cm|min|cat|l)(-|−)?\d*", re.IGNORECASE)
flowvalue = R("^\d+(\.|,|\d+)?")("flowvalue")
flownames = (R("GSHV", re.IGNORECASE) | R("SV", re.IGNORECASE) |(R("space", re.IGNORECASE) + R("velocity", re.IGNORECASE)))
GHSV = (flownames + SkipTo(flowvalue) + flowvalue + (flowunit + ZeroOrMore(flowunitafter | flowunitpre)).add_action(merge)(u'flowunit'))(u"textandunit")
numberonly = (flowvalue + (flowunit + ZeroOrMore(flowunitafter | flowunitpre)).add_action(merge)(u'flowunit'))("umberonly")

flow = (GHSV | numberonly)(u"flowphrase")





class FootGHSVParser(BaseParser):
    root = flow

    def __init__(self):
        pass

    def interpret(self, result, start, end):
        c = Compound()

        # print("flow footnote")
        # print(etree.tostring(result))
        # print()
        flowvalue = result.xpath('//flowvalue/text()')
        flowunit = result.xpath('//flowunit/text()')
        flowunit = "".join(flowunit)
        context = {}
        # print(flowvalue)
        # print(flowunit)
        if flowvalue and flowunit:
            context["footflow"] = flowvalue[0]
            context["footflowunit"] = flowunit
        if context:
            # print(context)
            c.conv.append(Conv(**context))
        yield c

unit = R("mass|wt|weight|mol|mole|m|vol")(u"value")

compname = (R("$composition", re.IGNORECASE))(u"phrase")
feedname = (R("mixture", re.IGNORECASE))(u"phrase")
conditionname = R("condition", re.IGNORECASE)(u"phrase")
conditionname = R("conditions?", re.IGNORECASE)(u"phrase")
compprefix = (compname | feedname)(u"prefix")

units = (unit + (R(u'%') | W(u"percent")))(u'compunits')
value = (R(u"^\d{1,2}(\.\d)?$"))(u'compvalue')


name = (R("H2") | R("H2O") | R("CO") | R("N2") | R("He"))(u"compname")
# comppre = (compprefix + OneOrMore(SkipTo(name) + name + SkipTo(value) + value + Optional(units)))("phrase")
precomp = (OneOrMore(value | name | Any()))(u"phrase")

comp = (precomp)('comp')

class FootCompParser(BaseParser):
    root = comp

    def __init__(self):
        pass

    def interpret(self, result, start, end):
        c = Compound()

        # print("comp footnote")
        # print(etree.tostring(result))

        context = {}

        vvalue = result.xpath('//compvalue/text()')
        vnames = result.xpath('//compvalue/following-sibling::compname[1]/text()' )

        vvalue = [float(i) for i in vvalue]
        # if sum(vvalue) > 100:
        #     vvalue = []

        # print("vvalues: ",vvalue)
        # print("vnames: ",vnames)

        nnames = result.xpath('//compname/text()')
        nvalue = result.xpath('//compname/following-sibling::compvalue[1]/text()' )
        nvalue = [float(i) for i in vvalue]
        # print("nvalue: ", nvalue)
        # print("nnames: ", nnames)
        # print(nvalue)
        sumto = find_subset(vvalue, 100)
        if sumto and len(nnames) == len(vvalue):
            sumvalues = []
            sumnames = []
            for i, number in enumerate(vvalue):
                if number in sumto:
                    sumvalues.append(number)
                    sumnames.append(nnames[i])
            # print(sumvalues)
            # print(sumnames)
        # print(result.xpath('//compname/text()'))
        # print(result.xpath('//compvalue/text()'))
        if sum(nvalue) > 100:
            nvalue = []

        if sumto and len(nnames) == len(vvalue):
            value = sumvalues
            names = sumnames
        elif len(vvalue) != 0 and len(vnames) == len(vvalue):
            value = vvalue
            names = vnames
        elif len(nvalue) != 0 and len(nnames) == len(nvalue):
            value = nvalue
            names = nnames

        else:
            value = False
            names = False
        compstring = ""
        if value and len(value) == len(names):
            values = [(value[i], names[i]) for i, j in enumerate(value)]
            context["comp"] = values

        string = str(etree.tostring(result))
        # print(string)
        # print("string")
        test = re.search(r"(<compname>(.{0,5}H2.{0,5})<\/compname>(.{0,5}(<SYM>\/<\/SYM>)|(<COLON>:<\/COLON>).{0,5})<compname>(.{0,5}CO.{0,5})<\/compname>)", string)
        test2 = re.search(r"(<compname>(.{0,5}CO.{0,5})<\/compname>(.{0,5}(<SYM>\/<\/SYM>)|(<COLON>:<\/COLON>).{0,5})<compname>(.{0,5}H2.{0,5})<\/compname>)", string)

        if test or test2:
            # print(test.group())
            # print("ratio found in caption")
            if test:
                matchlocation = (test.start() + test.end()) / 2
            elif test2:
                matchlocation = (test2.start() + test2.end()) / 2
                test = test2
            # print('//*[text()=' + test.group(2) +']/following-sibling::compvalue[1]/text()')
            following = result.xpath('//*[text()=\'' + test.group(2) +'\']/following-sibling::compvalue[1]/text()' )
            preceding = result.xpath('//*[text()=\''+ test.group(6) +'\']/preceding-sibling::compvalue[1]/text()' )
            # print(following)
            # print(preceding)
            if len(following) > 0:
                fol = re.search("<compvalue>" + following[0], string).start()
                # print("fol", fol)
            else:
                fol = 10000000
            if len(preceding) > 0:
                pre = re.search( preceding[0] + "<\/compvalue>", string).end()
                # print("pre", pre)
            else:
                pre = 10000000
            # print(matchlocation)
            # print(abs(matchlocation - fol))
            # print(abs(matchlocation - pre))
            # print(abs(matchlocation - fol) > abs(matchlocation - pre))
            if abs(matchlocation - fol) > abs(matchlocation - pre):
                value = preceding
                if re.search(r"<\/compvalue>((<COLON>:<\/COLON>)|(<SYM>\/<\/SYM>))<compvalue>", string):
                    firstvalue = result.xpath('//*[text() =\'' + test.group(2) +'\']/preceding-sibling::compvalue[2]/text()')
                    if len(firstvalue) > 0 and float(firstvalue[0]) != 0:
                        value = float(firstvalue[0]) / float(value[0])
                    else:
                        value = None
                        test2 = None
            else:
                value = following
                # print(re.search(r"<\/compvalue>((<COLON>:<\/COLON>)|(<SYM>\/<\/SYM>))<compvalue>", string))
                # print('//*[text() = \'' + test.group(2) +'\']/preceding-sibling::compvalue[2]/text()')
                if re.search(r"<\/compvalue>((<COLON>:<\/COLON>)|(<SYM>\/<\/SYM>))<compvalue>", string):
                    denominator = result.xpath('//*[text() =\'' + test.group(2) +'\']/following-sibling::compvalue[2]/text()')
                    if len(denominator) > 0 and float(denominator[0]) != 0:
                        value = float(value[0]) / float(denominator[0])
                    else:
                        value = None
            if type(value) == type([]) and len(value) > 0:
                value = value[0]
            elif type(value) == type([]) and len(value) == 0:
                value = None
            if value:
                context["comp"] = [value, test.group(2) + "/" + test.group(6)]


        if context:
            # print("caption comp")
            # print(context["comp"])
            c.conv.append(Conv(**context))
        yield c

units = (R(u'(atm|bar|Pa|mmhg|MP)', re.IGNORECASE)(u'units'))
value = (Optional(R('~')) + R(u'^\d+((\.|,)\d+)?')).add_action(merge)(u'value')
pres = (value + units)(u"presphrase")
class FootPressureParser(BaseParser):
    """"""
    root = pres

    def __init__(self):
        pass

    def interpret(self, result, start, end):
        context = {}
        # print("foot pressure")
        # print(etree.tostring(result))
        # print()
        c = Compound()

        context = {}
        presvalue = first(result.xpath('//value/text()'))
        presunit = first(result.xpath('//units/text()'))

        # print(presvalue)
        # print(presunit)

        context["pressure"] = presvalue
        context["presunits"] = presunit
        if context:
            c.conv.append(Conv(**context))
        yield c

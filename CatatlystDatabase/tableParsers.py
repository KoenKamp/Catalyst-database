import re
import lxml.etree as etree
from chemdataextractor.model import BaseModel, StringType, ListType, ModelType, Compound
from chemdataextractor.parse import R, I, W, Optional, merge, ZeroOrMore, join, SkipTo
from chemdataextractor.parse.base import BaseParser
from chemdataextractor.parse import ZeroOrMore, Any, OneOrMore, Start, End, Group, Not, T
from chemdataextractor.utils import first




# print("inside heading")
# print(etree.tostring(result))
# print()
class BET(BaseModel):
    value = StringType()
    unit = StringType(contextual=True)
Compound.bet = ListType(ModelType(BET))
class Flow(BaseModel):
    value = StringType()
    unit = StringType(contextual=True)
Compound.flow = ListType(ModelType(Flow))

class CAT(BaseModel):
    name = StringType()
Compound.catalyst_name = ListType(ModelType(CAT))

class Comp(BaseModel):
    values = ListType(StringType())
    unit = StringType(contextual=True)
Compound.comp = ListType(ModelType(Comp))

class Temp(BaseModel):
    value = StringType()
    unit = StringType()
Compound.temp = ListType(ModelType(Temp))

class Selectivity(BaseModel):
    value = StringType()
    unit = StringType(contextual=True)
class Conv(BaseModel):
    tempvalue = StringType(contextual=True)
    tempunits = StringType(contextual=True)
    convvalue = StringType()
    convtype = StringType(contextual=True)
    convunits = StringType(contextual=True)
    captioninfo = StringType(contextual=True)
    check = StringType(contextual=True)
    catname = StringType(contextual=True)
    captioncatname = StringType(contextual=True)
    comp = StringType(contextual=True)
    unit = StringType(contextual=True)
    flow = StringType(contextual=True)
    flowunit = StringType(contextual=True)
    footflow = StringType(contextual=True)
    footflowunit = StringType(contextual=True)
    pressure = StringType(contextual=True)
    presunits = StringType(contextual=True)
    tofvalue = StringType()
    yieldtest = StringType(contextual=True)
    selectivity = ListType(ModelType(Selectivity,contextual=True),contextual=True)
Compound.conv = ListType(ModelType(Conv))

supportstring = "ZnO|YSZ|ceria|alumina|silica|SBA|ZSM|CNT|Al2O3|MgO|CeO2|TiO2|CMK|MnO|Y2O3|ZrO2|Tb4O7|HfO2|La2O3|Co3O4|ThO2|SiO2|Fe2O3|Sm2O3|Mo2C|Gd2O3|Yb2O3|CaO|CuO|NiO"
symbolstring = "|Li|Be|Ne|Na|Mg|Al|Si|Cl|Ox|Ca|Sc|Ti|V|Cr|Mn|Fe|Co|Ni|Cu|Zn|Ga|Ge|As|Se|Br|Kr|Rb|Sr|Y|Zr|Nb|Mo|Tc|Ru|Rh|Pd|Ag|Cd|In|Sn|Sb|Te|Xe|Cs|Ba|La|Ce|Pr|Nd|Pm|Sm|Eu|Gd|Tb|Dy|Ho|Er|Tm|Yb|Lu|Hf|Ta|Re|Os|Ir|Pt|Au|Hg|Tl|Pb|Bi|Po|At|Rn|Fr|Ra|Ac|Th|Pa|Np|Pu|Am|Cm|Bk|Cf|Es|Fm|Md|No|Lr|Rf|Db|Sg|Bh|Hs|Mt|Ds|Rg|Cn|Nh|Fl|Mc|Lv|Ts|Og"
name = (R(u"^((\d|%)*("+symbolstring+"|" + supportstring + ")(?![a-z])(([A-Zα-ωΑ-Ω0-9\/\-,\.]|(wt.?))[a-zA-Z0-9α-ωΑ-Ω0-9\/\-,\.]*)?)"))
post = R("^([A-Z]|[0-9]|(wt.?)|"+symbolstring+u"|\/|-|\.|,|%|\(|\))+$") | T("SYM")
name = (name + ZeroOrMore(post))(u"name").add_action(merge)

catalyst = R("(Catalysts?)|(precursors?)|(abb)|(sample)|(abb)|(materials?)|(composition)", re.IGNORECASE)

class CatalystHeadingParser(BaseParser):
    root = catalyst
    def interpret(self, result, start, end):
        """"""
        # print("inside cat cell")
        # print(etree.tostring(result))
        # print()
        yield Compound()



class CatalystsCellParser(BaseParser):
    root = name

    def interpret(self, result, start, end):
        # print("inside cat cell")
        # print(etree.tostring(result))
        # print()
        # print("test")
        c = Compound(
            catalyst_name=[
                CAT(
                    name=first(result.xpath('text()')),
                )
            ]
        )
        yield c

flowunit = R(r"^(h(-|−)\d|ml|s|g|N|min|cm3|l|kg|mol|\\|cat|\/|:|\(|\)|<|>|[|]|,|\.|×)+(-|−)?(\d+)?$", re.IGNORECASE)(u'flowunit')

flowname = R("^flow", re.IGNORECASE) + Optional(flowunit)
GHSV = (R("GHSV", re.IGNORECASE) + Optional(flowunit))(u"textandunit") #space velocity, (residence time?)
space = (R("space", re.IGNORECASE) + R("velocity", re.IGNORECASE) + Optional(flowunit))(u"textandunit")
flow = (flowname | GHSV | space)(u"flowphrase")
flowheader = (flow + ZeroOrMore(SkipTo(flowunit) + flowunit).add_action(merge)('units'))("phrase")
flowvalue = R("^\d+((\.|,)\d+)*")("value")

flowcell = (flowvalue + ZeroOrMore(SkipTo(flowunit) + flowunit).add_action(merge)(u"units"))("phrase")


class FlowHeadingParser(BaseParser):
    root = flow

    def interpret(self, result, start, end):
        """"""

        # print("inside flow header")
        # print(etree.tostring(result))
        # print()
        if type(result) == type([]):
            for i in result:
                flowunits = first(i.xpath('//unit/text()'))
                if flowunits != None:
                    break
        else:
            flowunits = first(result.xpath('//unit/text()'))
        c = Compound()
        if flowunits:
            c.flow.append(
                Flow(unit=flowunits)
            )
        yield c



class FlowCellParser(BaseParser):
    root = flowcell

    def interpret(self, result, start, end):

        # print("inside flow cell")
        # print(etree.tostring(result))
        # print()
        c = Compound(
            flow=[
                Flow(
                    value=first(result.xpath('./value/text()')),
                    unit=first(result.xpath('./units/text()')),
                )
            ]
        )
        yield c

yieldhead = R("yield", re.IGNORECASE)(u"yieldheader")



#add CO header

unit = R(u"^(CO|H2|N2|He|/|-)*")(u"unit")
unit = (unit + ZeroOrMore(unit)).add_action(merge)
compname = (R("composition", re.IGNORECASE))(u"phrase")
feedname = (R("feed", re.IGNORECASE))(u"phrase")
mixturename = (R("mix", re.IGNORECASE))(u"phrase")
conditionname = R("condition", re.IGNORECASE)(u"phrase")
ratio = (R("H2") + Any() + R("CO")).add_action(merge) | R("H2/CO")(u"unit")
ratio2 = (R("CO") + Any() + R("H2")).add_action(merge) | R("CO/H2")(u"unit")

compounds = (R("H2") | R("CO") | R("He") | R("CH4"))(u"unit")
all = (compounds + (OneOrMore(Optional(R(":") | R(r"\\") | R(r"\/")) + compounds))).add_action(merge)(u'seperator')
comp = (compname | feedname | conditionname | mixturename | all |  ratio | ratio2)(u"compphrase")


class CompHeadingParser(BaseParser):
    root = comp

    def interpret(self, result, start, end):
        """"""
        compunits=[""]
        # print("inside comp header")
        # print(etree.tostring(result))
        # print()
        if len(result) == 1:
            compunits = first(result.xpath('//unit/text()'))
        elif len(result) > 1:
            for item in result:
                compunit = first(item.xpath('//unit/text()'))
                if compunit:
                    compunits[0] += compunit
            if compunits[0] == "":
                compunits = []
         # print(flowunits)
        else:
            compunits = []
        # print("comp header")
        if "/CO" in first(result.xpath('//compphrase/text()')) or ":CO" in first(result.xpath('//compphrase/text()')) :
            compunits = first(result.xpath('//compphrase/text()'))
        if "CO/H2" in first(result.xpath('//compphrase/text()')) or "CO:H2" in first(result.xpath('//compphrase/text()')):
            compunits = first(result.xpath('//compphrase/text()'))
        # print(compunits)
        # print(compunits)
        c = Compound()
        if compunits:
            c.comp.append(
                Comp(unit=compunits)
            )
        yield c

compvalue = (R("^\d+(\.|,|\d*)"))(u'compvalue')
name = (R("^H2$") | R("^H2O$") | R("^CO$")| R("^CO2$") | R("steam"))(u"compname")
rationame = ((R("H2") + Any() + R("CO")).add_action(merge) | R("H2/CO") | R("H2:CO"))(u"ratio")
tempunit = (Optional("(") + Optional(R(u'°')) + R(u'[CFK℃]')).add_action(merge)(u'tempunit')
pressureunit = (R(u'(atm|bar|Pa|mmhg|MP)',re.IGNORECASE))(u'presunit').add_action(merge)
# comppre = (compprefix + OneOrMore(SkipTo(name) + name + SkipTo(value) + value + Optional(units)))("phrase")
precomp = (OneOrMore(compvalue | name | tempunit | pressureunit | Any()))(u"phrase")
comp = (precomp)('comp')
class CompCellParser(BaseParser):
    root = comp

    def interpret(self, result, start, end):
        c = Compound()

        # print("comp cell")
        # print(etree.tostring(result))
        # print()

        c = Compound()

        if result.xpath('//presunit/text()'):
            context = {}
            presunit = first(result.xpath('//presunit/text()'))
            presvalue = first(result.xpath('//presunit/preceding-sibling::compvalue[1]/text()'))
            context['pressure'] = presvalue
            context['presunits'] = presunit
            c.conv.append(Conv(**context))


        if result.xpath('//tempunit/text()'):
            context = {}
            tempunit = first(result.xpath('//tempunit/text()'))
            tempvalue = first(result.xpath('//tempunit/preceding-sibling::compvalue[1]/text()'))
            context['tempvalue'] = tempvalue
            context['tempunits'] = tempunit
            c.conv.append(Conv(**context))
        context={}

        allvalues = result.xpath("//compvalue/text()")
        vvalue = result.xpath('//compvalue/text()')
        vnames = result.xpath('//compvalue/following-sibling::compname[1]/text()' )
        try:
            vvalue = [float(i) for i in vvalue]
        except:
            vvalue = []
        if sum(vvalue) > 100:
            vvalue = []

        # print("vvalues: ",vvalue)
        # print("vnames: ",vnames)

        nnames = result.xpath('//compname/text()')
        nvalue = result.xpath('//compname/following-sibling::compvalue[1]/text()' )
        try:
            nvalue = [float(i) for i in vvalue]
        except:
            nvalue = []
        # print("nvalue: ", nvalue)

        # print("nnames: ", nnames)
        # print(nvalue)
        # print(allvalues)
        if sum(nvalue) > 100:
            nvalue = []

        if len(vvalue) != 0 and len(vnames) == len(vvalue):
            value = vvalue
            names = vnames
        elif len(nvalue) != 0 and len(nnames) == len(nvalue):
            value = nvalue
            names = nnames

        elif len(allvalues) == 1:
            value = allvalues
            names = []
        else:
            value = []
            names = []
        # print(value)
        # print(names)
        if value and len(value) == len(names):
            values = [(value[i], names[i]) for i, j in enumerate(value)]
            context["values"] = values
        elif value and len(value) == 1 and len(names) < 1:
            context["values"] = value

        # print("table comp")
        print(context)
        if context:
            c.comp.append(Comp(**context))
        yield c

no = (R("calcin", re.IGNORECASE) | R("thermo", re.IGNORECASE) | R("equi", re.IGNORECASE)).hide()
prefix = (R("^temp", re.IGNORECASE) | R("^T[^OP]") | R("^T$"))("prefix")
units = (Optional(W(u'°')) + R(u'[CFK]'))(u'units').add_action(merge)
temp = (Optional(Not(no)) + SkipTo(prefix) + prefix + Optional(SkipTo(units) + units))(u"temp")

temphead = (temp)(u"tempphrase")

class TempHeadingParser(BaseParser):
    root = temphead

    def interpret(self, result, start, end):
        """"""
        # print("inside temp")
        # print(etree.tostring(result))
        # print()
        # print(lollol)
        tempunits = first(result.xpath('./units/text()'))

        c = Compound()
        if tempunits:
            c.temp.append(
                Temp(unit=tempunits)
            )
        yield c

units = (Optional(W(u'°')) + R(u'[CFK]'))(u'units').add_action(merge)
value = (Optional(R('~|>|<')) + R(u'^\d{2,4}'))(u'value').add_action(merge)
values = (value + Optional(R(",|-|\W") + value)).add_action(merge)
valueunit = (values + Optional(units))("phrase")


tempcell = (valueunit)(u"temperature")
class TempCellParser(BaseParser):
        root = tempcell

        def interpret(self, result, start, end):

            value = first(result.xpath('//value/text()'))
            c = Compound(
                temp=[
                    Temp(
                        value=value
                        )

                ]
            )
            yield c

tempvalue = (Optional(R('~|>|<')) + R(u'^\d{3,4}'))(u'tempvalue').add_action(merge)
tempunit = (Optional(W(u'°')) + R(u'[CFK]'))(u'tempunits').add_action(merge)

no = (R("equi", re.IGNORECASE) | R("rate", re.IGNORECASE))(u"no")
co = R("^CO", re.IGNORECASE)
prefix = R("^conv(?!erted)", re.IGNORECASE)
rate = Not(R("^rate"))
units = (R(u'%'))(u'convunits').add_action(merge)
any = Any()(u'any')
convname = (Optional(no | any) + SkipTo(prefix) + prefix + rate + Optional(SkipTo(tempvalue) + tempvalue + tempunit) + Optional(SkipTo(units) + units))(u"convname")
convother = (any + SkipTo(prefix) + prefix + rate + Optional(SkipTo(tempvalue) + tempvalue + tempunit) + Optional(SkipTo(units) + units))(u"convname")
convsymbol = (R("^X[^RPAH]") + Optional(SkipTo(units) + units))(u"conv")
numberonly = (tempvalue + tempunit)(u"tempnumber")
convhead = (convname |convother| convsymbol | numberonly)


class ConvHeadingParser(BaseParser):

    root = convhead
    def interpret(self, result, start, end):
        """"""
        context = {}
        c = Compound()
        no = first(result.xpath('./no/text()'))
        tempunits = first(result.xpath('./tempunits/text()'))
        context['tempunits'] = tempunits
        tempvalues = first(result.xpath('./tempvalue/text()'))
        context['tempvalue'] = tempvalues
        any = first(result.xpath('//any/text()'))
        context["convtype"] = any
        # print("inside conv heading")
        # print(etree.tostring(result))
        check = result.xpath('/tempnumber')
        # print("check: ", check)
        # print()
        if check:
            # print("yes")
            c.conv.append(Conv(**{'check': "True"}))
        if no == None:
            context['convunits'] = first(result.xpath('./convunits/text()'))
        else:
            context['convunits'] = first(result.xpath('./no/text()'))

        if tempunits or any:
            c.conv.append(
                Conv(**context)

            )
        yield c

tempunits = (Optional(W(u'°')) + R(u'[CFK]'))(u'tempunits').add_action(merge)
tempvalue = (Optional(R('~|>|<')) + R(u'^\d{3,4}'))(u'tempvalue').add_action(merge)

convunits = R("%")(u"convunits")
convvalue = (R(u'^\d+((\.|,)\d+)?')| R("100"))(u'convvalue')
valueunit = (convvalue + Optional(convunits) + Optional(SkipTo(tempvalue) + tempvalue + tempunits))("phrase")



convcell = (valueunit | tempphrase)(u"conversion")
class ConvCellParser(BaseParser):
        root = convcell

        def interpret(self, result, start, end):
            # for item in result:
            #     print("inside cell")
            #     print(etree.tostring(item))
            #     print()
            convvalue = first(result.xpath('//convvalue/text()'))
            convunits = first(result.xpath('//convunits/text()'))
            tempvalue = first(result.xpath('//tempvalue/text()'))
            tempunits = first(result.xpath('//tempunits/text()'))
            c = Compound(
                conv=[
                    Conv(
                        convvalue=convvalue,
                        convunits=convunits,
                        tempvalue=tempvalue,
                        tempunits=tempunits
                        )

                ]
            )
            yield c

tempvalue = (Optional(R('~|>|<')) + R(u'^\d{3,4}'))(u'tempvalue').add_action(merge)
tempunit = (Optional(W(u'°')) + R(u'[CFK]'))(u'tempunits').add_action(merge)

tofpre = R("TOF", re.IGNORECASE)("tof")
tofabb = (tofpre + Optional(SkipTo(tempvalue) + tempvalue + tempunit)).add_action(merge)(u"tofabb")

turnover = R("^turnover", re.IGNORECASE)(u"turnover")

frequency = R("^freq", re.IGNORECASE)(u"freq")
tofname = (turnover + frequency + Optional(SkipTo(tempvalue) + tempvalue + tempunit))(u"name")

tofhead = (tofabb | tofname)(u"tofphrase")

class TofHeadingParser(BaseParser):
    root = tofhead

    def interpret(self, result, start, end):

        # print("inside heading of tof")
        # print(etree.tostring(result))
        context = {}
        no = first(result.xpath('./no/text()'))
        context['tempunits'] = first(result.xpath('./tempunits/text()'))
        context['tempvalue'] = first(result.xpath('./tempvalue/text()'))
        if no == None:
            context['convunits'] = first(result.xpath('./convunits/text()'))
        else:
            context['convunits'] = first(result.xpath('./no/text()'))
        c = Compound()

        if tempunits:
            c.conv.append(
                Conv(**context)

            )
        yield c


tempunits = (Optional(W(u'°')) + R(u'[CFK]'))(u'tempunits').add_action(merge)
tempvalue = (Optional(R('~|>|<')) + R(u'^\d{3,4}'))(u'tempvalue').add_action(merge)


tofvalue = (R(u'^\d+((\.|,)\d+)?'))(u'tofvalue')
tofcell = (tofvalue + Optional(SkipTo(tempvalue) + tempvalue + tempunits))("phrase")

class TofCellParser(BaseParser):
        root = tofcell

        def interpret(self, result, start, end):
            # print("inside cell")
            # print(etree.tostring(result))
            # print()
            tofvalue = first(result.xpath('./tofvalue/text()'))
            tempvalue = first(result.xpath('./tempvalue/text()'))
            tempunits = first(result.xpath('./tempunits/text()'))
            c = Compound(
                conv=[
                    Conv(
                        tofvalue=tofvalue,
                        tempvalue=tempvalue,
                        tempunits=tempunits
                        )

                ]
            )
            yield c

prefix = (R("pressure", re.IGNORECASE) | R("pres") | R("^P[^a-zreRP]?"))
presunits = (R(u'(atm|bar|Pa|mmhg|MP)',re.IGNORECASE))(u'units').add_action(merge)
pres = (prefix + Optional(SkipTo(presunits) + presunits))(u"pres")

preshead = (pres)(u"presphase")

class PressureHeadingParser(BaseParser):
    root = preshead

    def interpret(self, result, start, end):
        """"""

        # print("inside heading of pres")
        # print(etree.tostring(result))
        presunits = first(result.xpath('//units/text()'))

        c = Compound()
        if presunits:
            c.conv.append(
                Conv(presunits=presunits)
            )
        yield c


value = (R(u'^\d+((\.|,)\d+)?'))(u'value').add_action(merge)
valueunit = (value + Optional(presunits))("phrase")


prescell = (valueunit)(u"pressurecell")
class PressureCellParser(BaseParser):
        root = prescell

        def interpret(self, result, start, end):
            pressure = first(result.xpath('//value/text()'))
            presunit = first(result.xpath('//units/text()'))
            if not pressure:
                pressure = first(result.xpath('//phrase/text()'))

            # print("inside cell of pres")
            # print(pressure)
            # print(presunit)
            c = Compound(
                conv=[
                    Conv(
                        pressure=pressure,
                        pressureunit=presunit
                        )

                ]
            )
            yield c


sunits = ((R('^(S)?(CO2?|CH).?(?!free)') | R(u'^(S)?C(\d|=)') | R("^(S)?(DME|Hc|Oxy|ROH|RH|MeOH|EtOH|PrOH|BuOH|MOH|EOH|POH|BOH|buthanol|propanol|C5OH|Methanol|ethanol|methane|ethane|carbonmonoxide|aromatics)", re.IGNORECASE)) + ZeroOrMore(Any()))(u'units').add_action(merge)
selectivity = (Start() + sunits)('phrase')


class SelectivityHeadingParser(BaseParser):
    root = selectivity

    def interpret(self, result, start, end):
        """"""
        # print("inside heading selectivity")
        # print(etree.tostring(result))
        # print()
        selectivityunits = first(result.xpath('//units/text()'))
        # print(selectivityunits)
        # print()
        c = Compound()
        if selectivityunits:
            sel = Selectivity(unit=selectivityunits)
            c.conv.append(Conv(selectivity=[sel]))

        # print(c.serialize())
        yield c


value = (R(u'^\d+((\.|,)\d)?'))(u'value').add_action(merge)
values = (value + Optional(R(",|-|\W") + value)).add_action(merge)
valueunit = (values + Optional(sunits))("selectivitycell")


scell = (valueunit)(u"pressurecell")
class SelectivityCellParser(BaseParser):
        root = scell

        def interpret(self, result, start, end):

            # print("inside cell selectivity")
            # print(etree.tostring(result))
            # print()
            value = result.xpath('./value/text()')
            sel = Selectivity(value=value)
            c = Compound()
            if value:
                c.conv.append(Conv(selectivity=[sel]))

            yield c


betunits = Optional(T("SYM")) + R(r"^(m|g|cm|\\|\/|:|\(|\)|<|>|[|]|,|\.|×)+(\d+)?")(u'betunit')
prefix = (R("BET", re.IGNORECASE) | (R("surface") + Optional(Any()) + R("area")) | R("surfacearea") | R('surface.area'))
betheader = (prefix + ZeroOrMore(SkipTo(betunits).hide() + betunits).add_action(merge)("units"))(u"phrase")

class BETHeaderParser(BaseParser):
    root = betheader

    def interpret(self, result, start, end):
        # """"""
        # print("inside bet header")
        # print(etree.tostring(result))
        # print()
        units = first(result.xpath('//units/text()'))
        # print(units)
        c = Compound(
            bet=[
                BET(
                    unit=units
                    )

            ]
        )
        yield c


value = (R(u'^\d+((\.|,)\d+)?'))(u'betvalue').add_action(merge)
valueunit = (value + (ZeroOrMore(SkipTo(betunits) + betunits))).add_action(merge)("betcell")


scell = (valueunit)(u"betcell")
class BETCellParser(BaseParser):
        root = scell

        def interpret(self, result, start, end):
            # print("inside betcell")
            # print(etree.tostring(result))
            # print()
            value = result.xpath('//betvalue/text()')
            if len(value) < 1:
                value = result.xpath("//betcell/text()")
            units = first(result.xpath('//units/text()'))
            #
            # print(value)
            # print(units)
            c = Compound(
                bet=[
                    BET(
                        value=value,
                        unit=units
                        )

                ]
            )
            yield c

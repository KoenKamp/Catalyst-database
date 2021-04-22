import os
from lxml import etree
import matplotlib.pyplot as plt
import pandas
from collections import Counter

path = r"C:\Users\Koen\Documents\Masterproject\xmllong\\"

nsmap={'ce': 'http://www.elsevier.com/xml/common/dtd'}
hist = []
for root, dirs, files in os.walk(path):
    for i,file in enumerate(files):
        print(file)
        root = etree.parse(path + file)
        for item in root.xpath('//ce:table-footnote', namespaces=nsmap):
            all_elements = list(item.iter())
            all_elements = [i.tag.split('}')[1] for i in all_elements]
            all_elements = list(dict.fromkeys(all_elements))
            hist += all_elements

letter_counts = Counter(hist)
df = pandas.DataFrame.from_dict(letter_counts, orient='index')
df.plot(kind='bar')
plt.show()

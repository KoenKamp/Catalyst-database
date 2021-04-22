 from setuptools import setup, find_packages

 setup(
   name='CatalystDatabase',
   version='0.1',
   author='Koen',
   author_email='koenk1@gmail.com',
   packages=find_packages(),
   scripts=['bin/script1','bin/script2'],
   url='http:/test.nl',
   license='MIT',
   description='automatic extraction of catalytic data from mostly tables',
   long_description=open('README.txt').read(),
   install_requires=[
   'pickle', 'lxml', 'pandas', 'matplotlib', 'numpy', 'appdirs', 'beautifulsoup4', 'click', 'cssselect', 'lxml', 'nltk', 'pdfminer.six', 'python-dateutil',
        'requests', 'six', 'python-crfsuite', 'DAWG', 'PyYAML'
   ],
)

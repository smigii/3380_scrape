import os
import pandas as pd

names = pd.read_csv("data/names2.csv")
size = len(names.index)
print(size)


'''
import pandas as pd
from bs4 import BeautifulSoup

f = open("html/nm0000001.html", 'r')

soup = BeautifulSoup(f.read(), 'lxml')

print(soup)
'''


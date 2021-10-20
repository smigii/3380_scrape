import pandas as pd
from bs4 import BeautifulSoup

f = open("html/nm0000001.html", 'r')

soup = BeautifulSoup(f.read(), 'lxml')

print(soup)

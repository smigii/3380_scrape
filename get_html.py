import requests
import pandas as pd
from bs4 import BeautifulSoup

#num = 71

names = pd.read_csv("data/IMDb_names.csv").dropna(how='all', subset=['spouses_string']).reset_index(drop=True)

url_prefix = "https://www.imdb.com/name/"
url_postfix = "/bio"

print(f"Total, {len(names.index)}")

err_log = open("errlog", 'w+')

for i in range(len(names.index)):
#for i in range(20):

	nameID = names['imdb_name_id'][i]
	url = url_prefix + nameID + url_postfix
	try:
		src = requests.get(url).text
		soup = BeautifulSoup(src, 'lxml')
		fam = soup.find("table", {"id": "tableFamily"}).prettify()

		fout = open("html/"+nameID+".html", 'w+')
		fout.write(str(fam))
		fout.close()

		if i % 100 == 0:
			print(i)

	except:
		err_log.write("Fuckup: " + nameID)

# print(soup.find("table", {"id": "tableFamily"}).prettify())

# print(soup.prettify())

'''
nmID1, name1, nmID2, name2, start, end, end_reason
nmID2 could be null 
'''
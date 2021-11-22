import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import os

fblacklist = open("logs/err_log", "r")
blacklist = fblacklist.readlines()
for i in range(len(blacklist)):
	blacklist[i] = blacklist[i][:-1]
blacklist = set(blacklist)
fblacklist.close()

df = pd.read_csv("data/names2.csv")
dfnames = set(df["imdb_name_id"].tolist())
donezo = set(os.listdir("html"))

names = list(dfnames - donezo - blacklist)
print(f"dfnames: {len(dfnames)}, donezo: {len(donezo)}, blacklist: {len(blacklist)}")

url_prefix = "https://www.imdb.com/name/"
url_postfix = "/bio"

start = time.time()
total_time = 0
pcent = 0
err_log = open("logs/err_log", 'a+')
out_log = open("logs/err_log", 'w+')
size = len(names)
inc = 100
counter = 0

print(f"Total, {size}")
print("Starting!")

for i in range(size):

	nameID = names[i]
	url = url_prefix + nameID + url_postfix
	counter += 1

	try:
		src = requests.get(url).text
		soup = BeautifulSoup(src, 'lxml')
		fam = soup.find("table", {"id": "tableFamily"}).prettify()

		fout = open("html/"+nameID, 'w+')
		fout.write(str(fam))
		fout.close()

	except:
		err_log.write(nameID + "\n")

	if counter >= inc:
		counter = 0
		end = time.time()
		dt = end - start
		total_time += dt
		pcent = round(100 * i / size)
		string = format(f"{pcent}% -- {i}/{size} -- Elapsed: {total_time / 60:.3f} mins -- Delta: {dt / 60:.3f} mins -- Remaining: {((total_time * 1.0/(float(i)/float(size))) / 60):.3f} mins")
		out_log.write(string + "\n")
		print(string)
		start = time.time()



err_log.close()
out_log.close()

# 53143  2619
# dfnames: 72464, donezo: 47758, blacklist: 2235

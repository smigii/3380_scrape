import os
import pandas as pd
from bs4 import BeautifulSoup

# Dataframes to export
df_spouses = pd.DataFrame(columns=["imdb_id", "spouse_id", "spouse_name", "s_year", "s_month", "s_day", "e_year", "e_month", "e_day", "e_reason", "n_kids"])
df_children = pd.DataFrame(columns=["imdb_id", "child_id", "child_name"])
df_parents = pd.DataFrame(columns=["imdb_id", "parent_id", "parent_name"])
df_relatives = pd.DataFrame(columns=["imdb_id", "relative_id", "relative_name", "relation"])

# Open and get html table data
imdb_id = "nm0000014"
f = open("html/" + imdb_id)
soup = BeautifulSoup(f.read(), 'lxml')

# Split table rows
rows = soup.find_all("tr")

# Process
for row in rows:

	# Each row will be one of spouse, children, parent or relatives
	# Each row has first column specifying section, second column
	# containing <br/> separated list.

	columns = row.find_all("td")

	# First <td> tells us which section it is
	section = columns[0].text.strip()

	if section == "Spouse":
		print("Spouse!")

	elif section == "Children":
		# [4:-5] removes the <td> and </td> tags
		children = str(columns[1])[4:-5].split('<br/>')

		for child in children:
			# ---------------------- Yikes -----------------------
			sub_soup = BeautifulSoup(child.strip(), 'html.parser')

			if len(sub_soup.find_all("a")) == 0:
				# Non-linked entries are stored [lastname, firstname]
				child_name = child.split(',')
				child_name = [name.strip() for name in child_name]
				child_name.reverse()
				child_name = ' '.join(child_name)
				df_children.loc[len(df_children)] = [imdb_id, "", child_name]

			else:
				imdb_id_2 = sub_soup.find("a", href=True)["href"].replace("/name/", '')
				df_children.loc[len(df_children)] = [imdb_id, imdb_id_2, sub_soup.text.strip()]

	elif section == "Parents":
		print("Parents!")

	elif section == "Relatives":
		print("Relatives!")

	else:
		print("Oh fuck!")

#str(x[1].find_all("td")[1])[4:-5].split('<br/>')


# Export dataframes
df_spouses.to_csv("out/spouses.csv", index=False)
df_children.to_csv("out/children.csv", index=False)
df_parents.to_csv("out/parents.csv", index=False)
df_relatives.to_csv("out/relatives.csv", index=False)

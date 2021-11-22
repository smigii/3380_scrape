import os
import pandas as pd
from bs4 import BeautifulSoup


# -----------------------------------------------------------------------------
# ----- Functions -------------------------------------------------------------
# -----------------------------------------------------------------------------


def extract_children_parents(data, df, key_id):
	"""
	:param data: <td> wrapped soup containing section data
	:param df: DataFrame to update
	:param key_id: Current imdb id being processed
	"""

	# [4:-5] removes the <td> and </td> tags
	list_family = str(data)[4:-5].split('<br/>')

	for person in list_family:

		sub_soup = BeautifulSoup(person.strip(), 'html.parser')

		# Check if the person is in anchor tag (in imdb database)
		if len(sub_soup.find_all("a")) == 0:
			# Non-linked entries are stored [lastname, firstname]
			person_name = person.split(',')
			person_name = [name.strip() for name in person_name]
			person_name.reverse()
			person_name = ' '.join(person_name)
			df.loc[len(df)] = [key_id, "", person_name]

		else:
			imdb_id_person = sub_soup.find("a", href=True)["href"].replace("/name/", '')
			df.loc[len(df)] = [key_id, imdb_id_person, sub_soup.text.strip()]


def extract_relatives(data, df, key_id):
	"""
	:param data: <td> wrapped soup containing section data
	:param df: DataFrame to update
	:param key_id: Current imdb id being processed
	"""

	# [4:-5] removes the <td> and </td> tags
	relatives = str(data)[4:-5].split('<br/>')

	for relative in relatives:

		sub_soup = BeautifulSoup(relative, 'html.parser')

		# Check if the person is in anchor tag (in imdb database)
		if len(sub_soup.find_all("a")) == 0:
			# Non-linked entries are stored [lastname, firstname\n (relation)]
			content = relative.strip().split('\n')

			relation = ""
			if len(content) > 1:
				relation = content[1].strip().strip('()')

			person_name = content[0].split(',')
			person_name = [name.strip() for name in person_name]
			person_name.reverse()
			person_name = ' '.join(person_name)

			df.loc[len(df)] = [key_id, "", person_name, relation]

		else:
			relation = ""
			relation_split = relative.strip().split('</a>')
			if len(relation_split) > 1:
				relation = relation_split[1].strip().strip('()')

			anchor = sub_soup.find("a", href=True)
			imdb_id_person = anchor["href"].replace("/name/", '')

			df.loc[len(df)] = [key_id, imdb_id_person, anchor.text.strip(), relation]


# -----------------------------------------------------------------------------
# ----- Main ------------------------------------------------------------------
# -----------------------------------------------------------------------------


# Dataframes to export
df_spouses = pd.DataFrame(columns=["imdb_id", "spouse_id", "spouse_name", "s_year", "s_month", "s_day", "e_year", "e_month", "e_day", "e_reason", "n_kids"])
df_children = pd.DataFrame(columns=["imdb_id", "child_id", "child_name"])
df_parents = pd.DataFrame(columns=["imdb_id", "parent_id", "parent_name"])
df_relatives = pd.DataFrame(columns=["imdb_id", "relative_id", "relative_name", "relation"])

# Open and get html table data
# imdb_id = "nm0000226"  # Will Smith
imdb_id = "nm0565250"  # Melissa McCarthy, famous relatives
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
		extract_children_parents(columns[1], df_children, imdb_id)

	elif section == "Parents":
		extract_children_parents(columns[1], df_parents, imdb_id)

	elif section == "Relatives":
		extract_relatives(columns[1], df_relatives, imdb_id)

	else:
		print("Oh fuck!")

f.close()

df_spouses.to_csv("out/spouses.csv", index=False)
df_children.to_csv("out/children.csv", index=False)
df_parents.to_csv("out/parents.csv", index=False)
df_relatives.to_csv("out/relatives.csv", index=False)

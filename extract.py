import os
import pandas as pd
from bs4 import BeautifulSoup


# -----------------------------------------------------------------------------
# ----- Functions -------------------------------------------------------------
# -----------------------------------------------------------------------------


def clean_non_anchor_name(filthy_name):
	"""
	Takes in a white-space infested, backwards name string (WITHOUT anchor tags)
	and returns the cleaned string.

	' /n  /t   LastName, FirstName  /n' -> 'FirstName LastName'

	:param filthy_name: Gross name string
	:return: Cleaned name string
	"""
	clean_name = filthy_name.split(',')
	clean_name = [name.strip() for name in clean_name]
	clean_name.reverse()
	clean_name = ' '.join(clean_name)
	return clean_name


def extract_simple(data):
	"""
	Extracts a list of records containing the names, ids and other information
	from a <td> enclosed section of data

	:param data: td wrapped soup containing section data
	:return: List of dictionaries with keys {name, id, paren}
	"""

	out = []

	# [4:-5] removes the <td> and </td> tags
	people = str(data)[4:-5].split('<br/>')

	for person in people:

		record = {"id": "", "name": "", "paren": ""}

		sub_soup = BeautifulSoup(person, 'html.parser')

		# Check if the person is in anchor tag (in imdb database)
		if len(sub_soup.find_all("a")) == 0:

			# Non-linked entries are stored [{whitespace}lastname, firstname\n (paren_data){whitespace}]
			# (paren_data) may or may not be present

			content = person.strip().split('\n')

			paren_data = ""
			if len(content) > 1:
				paren_data = content[1].strip().strip('()')

			person_name = clean_non_anchor_name(content[0])

			record["name"] = person_name
			record["paren"] = paren_data

		else:
			paren_data = ""
			relation_split = person.strip().split('</a>')
			if len(relation_split) > 1:
				paren_data = relation_split[1].strip().strip('()')

			anchor = sub_soup.find("a", href=True)
			imdb_id_person = anchor["href"].replace("/name/", '')

			record["id"] = imdb_id_person
			record["name"] = anchor.text.strip()
			record["paren"] = paren_data

		out.append(record)

	return out


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
		children = extract_simple(columns[1])
		for c in children:
			df_children.loc[len(df_children)] = [imdb_id, c["id"], c["name"]]

	elif section == "Parents":
		parents = extract_simple(columns[1])
		for p in parents:
			df_parents.loc[len(df_parents)] = [imdb_id, p["id"], p["name"]]

	elif section == "Relatives":
		relatives = extract_simple(columns[1])
		for r in relatives:
			df_relatives.loc[len(df_relatives)] = [imdb_id, r["id"], r["name"], r["paren"]]

	else:
		print("Oh fuck!")

f.close()

df_spouses.to_csv("out/spouses.csv", index=False)
df_children.to_csv("out/children.csv", index=False)
df_parents.to_csv("out/parents.csv", index=False)
df_relatives.to_csv("out/relatives.csv", index=False)

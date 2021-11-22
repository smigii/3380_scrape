import os
import pandas as pd
from bs4 import BeautifulSoup


# Ugh
months = {
	"january": 1,
	"february": 2,
	"march": 3,
	"april": 4,
	"may": 5,
	"june": 6,
	"july": 7,
	"august": 8,
	"september": 9,
	"october": 10,
	"november": 11,
	"december": 12,
}


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


def extract_name_paren(person):
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

	return record


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
		record = extract_name_paren(person)
		out.append(record)

	return out


def extract_spouse(data):
	"""
	Extracts a list of records containing marriage-specific data
	from a <td> enclosed section of data.

	:param data: td wrapped soup containing section data
	:return: List of dictionaries with keys {id, name, s_year, s_month, s_day,
		e_year, e_month, e_day, e_reason, n_kids}
	"""
	out = []

	# [4:-5] removes the <td> and </td> tags
	spouses = str(data)[4:-5].split('<br/>')

	for spouse in spouses:

		record = {
			"id": "", "name": "",
			"s_year": "", "s_month": "", "s_day": "",
			"e_year": "", "e_month": "", "e_day": "",
			"e_reason": "", "n_kids": ""
		}

		# [name, (date - date), (end reason), (num_children)]
		content = str(spouse).split('(')

		# Get name data
		name_data = extract_name_paren(content[0])
		record["id"] = name_data["id"]
		record["name"] = name_data["name"]

		# Next field should always be dates.
		# Remove everything after closing paren, split
		# into 2 dates
		content = content[1:]
		dates = content[0].split(')')[0]
		dates = BeautifulSoup(dates, 'html.parser').text.split('-')
		d_from = dates[0].split()
		d_from = None if len(d_from) != 3 else d_from
		d_to = dates[1].split() if len(dates) > 1 else None
		d_to = None if d_to is not None and len(d_to) != 3 else d_to

		if d_from is not None:
			record["s_day"] = d_from[0]
			m = d_from[1].lower()
			record["s_month"] = months[m] if m in months else ""
			record["s_year"] = d_from[2]

		if d_to is not None:
			record["e_day"] = d_to[0]
			m = d_to[1].lower()
			record["e_month"] = months[m] if m in months else ""
			record["e_year"] = d_to[2]

		# Remaining could be e_reason or n_kids
		content = content[1:]

		for field in content:
			field = field.split(')')[0].strip()

			# If there is a digit in the field, we are (likely)
			# dealing with n_kids
			field_digits = [x for x in field if x.isdigit()]
			if len(field_digits) > 0:
				record["n_kids"] = field_digits[0]

			else:
				record["e_reason"] = field

		out.append(record)

	return out


# -----------------------------------------------------------------------------
# ----- Main ------------------------------------------------------------------
# -----------------------------------------------------------------------------


if __name__ == "__main__":

	df_spouses = pd.DataFrame(columns=["imdb_name_id", "spouse_id", "spouse_name", "s_year", "s_month", "s_day", "e_year", "e_month", "e_day", "e_reason", "n_kids"])
	df_children = pd.DataFrame(columns=["imdb_name_id", "child_id", "child_name"])
	df_parents = pd.DataFrame(columns=["imdb_name_id", "parent_id", "parent_name"])
	df_relatives = pd.DataFrame(columns=["imdb_name_id", "relative_id", "relative_name", "relation"])

	"""
	nm0000226 Will Smith
	nm0565250 Melissa McCarthy
	nm1176985 Dave Bautista
	"""
	#for i, imdb_id in enumerate(["nm0000226"]):
	for i, imdb_id in enumerate(os.listdir("html")):

		if i % 100 == 0:
			print(i)

		f = open("html/" + imdb_id)
		soup = BeautifulSoup(f.read(), 'lxml')

		rows = soup.find_all("tr")

		for row in rows:

			# Each row will be one of spouse, children, parent or relatives
			# Each row has first column specifying section, second column
			# containing <br/> separated list.

			columns = row.find_all("td")

			# First <td> tells us which section it is
			section = columns[0].text.strip()

			if section == "Spouse":
				spouses = extract_spouse(columns[1])
				for s in spouses:
					df_spouses.loc[len(df_spouses)] = [
						imdb_id, s["id"], s["name"],
						s["s_year"], s["s_month"], s["s_day"],
						s["e_year"], s["e_month"], s["e_day"],
						s["e_reason"], s["n_kids"],
					]

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

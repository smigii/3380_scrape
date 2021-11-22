# IMDb Movie Dataset Extension

This dataset extends the [IMDb Movies Dataset](https://www.kaggle.com/stefanoleone992/imdb-extensive-dataset?select=IMDb+movies.csv)
by adding the relationships between people in the names2.csv file.
This is a subset of IMDb_names.csv, where each name satisfying all of

1. name worked on a movie made during or after 1950
2. name worked on a movie with either a non-null worldwide or non-null domestic box office
3. name worked on a movie that has english as a listed language

is in names2.csv, which contains roughly 72k names. Of those 72k, 49k had a bio section on
IMDb, and so this dataset contains information on ***49735*** people.
The restriction was needed to cut down on scraping time.

## Files

|File|Description|
|----|-----------|
|data.zip|Base data from the kaggle dataset and names2.csv.|
|html.zip|Contains 72k files, named by IMDb name id. Contains the html *bio* table of each artist.|
|relationships.zip|4 relationship CSV files, spouses, relatives, children and parents|

## Output CSV Headers

1. spouses.csv
   * imdb_name_id - IMDb artist ID
   * spouse_id - IMDb artist ID (spouse)
   * spouse_name - guess
   * s_year - Marriage start year
   * s_month - Marriage start month
   * s_day - Marriage start day
   * e_year - Marriage end year
   * e_month - Marriage end month
   * e_day - Marriage end day
   * e_reason - Reason for end of marriage
   * n_kids - Number of children from marriage
   * Note: If IMDb did not specify year, month AND day for either
     start date, all three fields will simply be null. (same for end date)
2. relatives.csv
   * imdb_name_id - IMDb artist ID
   * relative_id - IMDb artist ID (relative)
   * relative_name - guess
   * relation - How are they related? (sibling, niece, etc.)
3. children.csv
   * imdb_name_id - IMDb artist ID
   * child - IMDb artist ID (child)
   * child_name - guess
4. parents.csv
   * imdb_name_id - IMDb artist ID
   * parent_id - IMDb artist ID (parent)
   * parent_name - guess

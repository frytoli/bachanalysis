# The Bachelor/Bachelorette Contestant Feature Analysis

![](https://media0.giphy.com/media/6wk5cC8J7ZEe8RR75e/giphy.gif)

DSCI-510 Final Project

Compare the features and place (the number of episodes the contestant was on the show for) of past contestants of ABC's The Bachelor and The Bachelorette.

## Data sets:

1. General data about the shows
   1. Data about The Bachelor
   2. Data about The Bachelorette shows
2. General data about the shows' seasons
   1. Data about The Bachelor seasons
   2. Data about The Bachelorette seasons
3. Data about The Bachelor and The Bachelorette contestants
4. Instagram data from contestants
5. Granular contestant data compiled from "transformed" data from the other data sets, including measured physical features and quantified "overall attractiveness" from known algorithms

## Data Models and Data Storage

### Data Class

The data is modeled as JSON data. The models for each data set (including subsets) are as follows:

Data sets 1.1 and 1.2:
```
{
  'season': 0, # -1 for null
  'original_run': '', # '' for null
  'suitor': '', # '' for null
  'winner': '', # '' for null
  'runnersup': '', # '' for null
  'proposal': 0, # 0 for no, 1 for yes, -1 for null
  'show': 0, # 0 for Bachelor, 1 for Bachelorette, -1 for null
  'still_together': 0, # 0 for no, 1 for yes, -1 for null
  'relationship_notes':'' # '' for null
}
```

Data sets 2.1 and 2.2:
```
{
  'name': '', # '' for null
  'age': 0, # -1 for null
  'hometown': '', # '' for null
  'occupation': '', # '' for null
  'eliminated': '', # '' for null
  'season': 0, # -1 for null
  'show': 0, # 0 for Bachelor, 1 for Bachelorette, -1 for null
  'profile_url': '',
  'place': 0 # -1 for null
}
```

Data set 3:
```
{
  'name': '', # '' for null
  'photo': '', # '' for null
  'born': '', # '' for null
  'hometown': '', # '' for null
  'occupation': '', # '' for null
  'seasons': '', # '' for null
  'social_media': '', # '' for null
  'height': '' # '' for null
}
```

Data set 4:
```
{
  TBD
}
```

Data set 5:
```
{
  'name': '', # '' for null
  'face_photo': '' # '' for null
}
```

#### Methods

get_sql_table_values(ds)

model_one(ds, data)

model_many(ds, datas)

### DB Class

Data is stored in a SQL database. The structure of this database, as defined by the data model, is as follows:
```
Placeholder for database diagram (including relationships)
```

## Collection

Collect data sets, facilitate the modeling of raw data, and facilitate the insertion of modeled data into data storage (SQL database).

### How to Run

Build the docker container:
```
docker build collection/ --tag bach
```

#### Arguments:

* set: Required. An integer associated with the desired data set to be collected. This can be a list of integers.
* source: Optional. Default: "remote". The location from where to collect the data for the data set(s) -- local or remote. (local files must be named raw{ds}.json where ds is the number associated with the data set, i.e. raw2.json)
* season: Optional. Default: all seasons (via data sets 1.1 and 1.2). An integer or list of integers associated with a desired season to collect data on. Only applicable with data set 2.
* contestant: Optional. Default: all contestants (via data sets 2.1 and 2.2). A case insensitive string or list of case insensitive strings associated with the first and last name separated by a "_" of a contestant from any season of The Bachelor or Bachelorette or the URL of a contestant's profile page on the [Bachelor Nation Fandom Wiki](https://bachelor-nation.fandom.com). Only applicable with data set 3.
* overwrite: Optional. Default: False. Overwrite any previously saved information from a data set in the database (dump and create a new table). Applicable with all data sets.

#### Examples:

Collect all available data for all data sets overwrite any old data from these data sets (drop and create new ds1, ds2, and ds3 tables) in the database:
```
docker run --volume $(pwd):/home/ bach collect.py 1 2 3 --overwrite
```

Collect data from The Bachelor/Bachelorette season 14:
```
docker run --volume $(pwd):/home/ bach collect.py 2 --season 14
```

Collect data about The Bachelorette contestant Dale Moss:
```
docker run --volume $(pwd):/home/ bach collect.py 3 --contestant dale_moss
```

Collect data about The Bachelor contestant Cassie Randolph:
```
docker run --volume $(pwd):/home/ bach collect.py 3 --contestant "https://bachelor-nation.fandom.com/wiki/Cassie_Randolph"
```

Collect data from all contestants from all seasons of The Bachelor/Bachelorette and source the data from a local location (./local/raw2.json):
```
docker run --volume $(pwd):/home/ bach collect.py 2 --source local
```

Collect all available data for data sets 1 and 2 and overwrite any old data from these data sets (drop and create new ds1 and ds2 tables) in the database:
```
docker run --volume $(pwd):/home/ bach collect.py 1 2 --overwrite
```

Collect all available data for data sets 1 and 2, collection available data from The Bachelor/Bachelorette seasons 8, 9, and 10, collect available data about contestants Naomi Crespo and Derek Peth, source the data from remote locations, and overwrite any old data in the pertinent database tables (drop and create new ds1, ds2, and ds3 tables):
```
docker run --volume $(pwd):/home/ bach collect.py 1 2 3 --season 8 9 10 --contestant naomi_crespo derek_peth --source remote --overwrite
```

## Transformation

Create a fifth data by applying transformation methods to data from the other data sets. This fifth data set will contain more granular data of each candidate and will be the data set primarily referenced during analysis.

### Transformations

crop_face(b64photo)

eval_rule_of_thirds(b64face)

eval_rule_of_fifths(b64face)

eval_golden_ratio(b64face)

eval_feature_sizes(b64face)

### How to Run

Build the docker container:
```
docker build collection/ --tag bach
```

#### Arguments:

* contestant: Optional. Default: all contestants (via data sets 2.1 and 2.2). A case insensitive string or list of case insensitive strings associated with the first and last name separated by a "_" of a contestant from any season of The Bachelor or Bachelorette.
* overwrite: Optional. Default: False. Overwrite any previously saved information from a data set in the database (dump and create a new table). Applicable with all data sets.

#### Examples:

Create data set 5 by transforming data from the other data sets and overwrite any old data from these data sets (drop and create a new ds5 table) in the database:
```
docker run --volume $(pwd):/home/ bach transform.py --overwrite
```

Transforming data from the other data sets for The Bachelorette contestant Dale Moss and overwrite any old data from these data sets (drop and create a new ds5 table) in the database:
```
docker run --volume $(pwd):/home/ bach transform.py --contestant dale_moss --overwrite
```

## Analysis

To-do

## Tasks

### Project Outline and Data Set Identification

- [x] Create Github repo
- [x] Identify data sets
  - [x] Info of all Bachelor seasons: https://en.wikipedia.org/wiki/The_Bachelor_(American_TV_series)
  - [x] Info of all Bachelorette seasons: https://en.wikipedia.org/wiki/The_Bachelorette
  - [x] Info and place of all Bachelor contestants: https://en.wikipedia.org/wiki/The_Bachelor_(season_1) (enumerate seasons)
  - [x] Info and place of all Bachelorette contestants: https://en.wikipedia.org/wiki/The_Bachelorette_(season_1) (enumerate seasons)
  - [x] Info of all Bachelor/Bachelorette cast members: https://bachelor-nation.fandom.com/wiki/Alex_Michel (enumerate names)
- [ ] Project outline

### Collect Data

- [x] Build scrapers
  - [x] Wikipedia scraper
    - [x] Data sets 1.1 and 1.2
    - [x] Rename '#' column
  - [x] Bachelor Nation scraper
    - [x] Data sets 2.1, 2.2, and 3
  - [ ] Instagram scraper
    - [ ] Data set(s) 4(.?)
- [x] Multiprocess
- [x] Options
  - [x] Source
  - [x] Seasons
  - [x] Contestants
  - [x] Overwrite
- [x] Dockerize
- [ ] Collect all the datas!

### Model and Store Data

- [x] Model data
  - [x] Create data models for data sets
  - [x] Data class that takes-in raw json data, models it according to the data set, and outputs a structured data set
    - [x] Data sets 1.1 and 1.2 (Wikipedia)
      - [x] Rename '#' column to 'Season'
      - [x] Add 'show' column
    - [x] Data sets 2.1 and 2.2 (Bachelor Nation)
      - [x] Add 'profile_url' column
      - [x] Add 'show' column
      - [x] Add 'season' column
    - [x] Data set 3 (Bachelor Nation)
    - [ ] Write data set data from database to an output file
- [x] Data storage (SQL database)
  - [x] DB class that interacts with SQL database
    - [x] Create tables with input list of column tuples
    - [x] Take in pre-modeled json data (formatted by data class) and input it into given data source table
    - [x] Retrieve data from database (account for columns and filters)
    - [x] Retrieve max of data in column from database (account for filters)

### Analysis and Conclusions

- [ ] Output data to file
- [ ] Analyze data and draw conclusions
  - [ ] How should I handle missing data?

# The Bachelor/Bachelorette Contestant Physical Attribute Analysis

![](https://media0.giphy.com/media/6wk5cC8J7ZEe8RR75e/giphy.gif)

DSCI-510 Final Project

Compare the physical features and place (the number of episodes the contestant was on the show for) of past contestants of ABC's The Bachelor and The Bachelorette.

## How to Run

### Collection

#### Data source numbers:

1. General info of all Bachelor seasons
2. General info of all Bachelorette seasons
3. General info and place of all Bachelor contestants
4. General info and place of all Bachelorette contestants
5. Photos and additional physical info of all Bachelor/Bachelorette cast members

#### Arguments:

* scraper: Required. An integer associated with the desired scraper to be executed. This can be a list of integers.
* season: Optional. An integer or list of integers associated with a desired season to collect data on. Only applicable with data sources 3 and 4.
* contestant: Optional. Default: A case insensitive string or list of case insensitive strings associated with the first and last name separated by a "_" of a contestant from any season of The Bachelor or Bachelorette. Only applicable with data source 5.
* file: Optional. Output retrieved data to a file in ./data/. Note that all retrieved data is ALWAYS inserted into a database, including when this flag is specified. Applicable with all data sources.
* overwrite: Optional. Overwrite any previously saved information from a data source in the database (dump and create a new data source table). Applicable with all data sources.

#### Examples:

Collect all available data from all sources:
```
docker build collection/ --tag collection
docker run --volume $(pwd):/home/ collection 1 2 3 4 5
```

Collect data from The Bachelor season 14:
```
docker build collection/ --tag collection
docker run --volume $(pwd):/home/ collection 3 --season 14
```

Collect data about The Bachelorette contestant Dale Moss:
```
docker build collection/ --tag collection
docker run --volume $(pwd):/home/ collection 5 --contestant dale_moss
```

Collect data from all contestants from all seasons of the Bachelor and write the data to a json file located in ./data/ (data is still inserted into the database):
```
docker build collection/ --tag collection
docker run --volume $(pwd):/home/ collection 3 --file
```

Collect all available data from sources 1 and 2 and overwrite any old data in the database:
```
docker build collection/ --tag collection
docker run --volume $(pwd):/home/ collection 1 2 --overwrite
```

Collect all available data from sources 1 and 2, collection available data from The Bachelorette seasons 8, 9, and 10, collect available data about contestants Naomi Crespo and Derek Peth, output all retrieved data to associated files (these will be ./data/ds1.json, ./data/ds2.json, ./data/ds4.json, and ./data/ds5.json), and overwrite any old data in the pertinent database tables (tables: ds1, ds2, ds4, and ds5):
```
docker build collection/ --tag collection
docker run --volume $(pwd):/home/ collection 1 2 4 5 --season 8 9 10 --contestant naomi_crespo derek_peth --file --overwrite
```

## To-Do

### Project Outline and Data Set Identification

- [x] Create Github repo
- [x] Identify data sets
  - [x] General info of all Bachelor seasons: https://en.wikipedia.org/wiki/The_Bachelor_(American_TV_series)
  - [x] General info of all Bachelorette seasons: https://en.wikipedia.org/wiki/The_Bachelorette
  - [x] General info and place of all Bachelor contestants: https://en.wikipedia.org/wiki/The_Bachelor_(season_1) (enumerate seasons)
  - [x] General info and place of all Bachelorette contestants: https://en.wikipedia.org/wiki/The_Bachelorette_(season_1) (enumerate seasons)
  - [x] Photos and height (not complete) of all Bachelor/Bachelorette cast members: https://bachelor-nation.fandom.com/wiki/Alex_Michel (enumerate names)
- [ ] Project outline

### Collect Data

- [x] Build scrapers
  - [x] Data source 1 scraper
    - [x] Rename '#' column
  - [x] Data source 2 scraper
    - [x] Rename '#' column
  - [x] Data source 3 scraper
    - [x] Rename 'Job' column
  - [x] Data source 4 scraper
    - [x] Rename 'Job' column
  - [x] Data source 5 scraper
    - [x] Scrape photo
    - [x] Scrape personal info
    - [x] Scrape additional personal info (i.e. height)
- [x] Multiprocess
- [x] Options
  - [x] Seasons
  - [x] Contestants
  - [x] Output format (this will tie-in to the "Model and Store Data" phase)
  - [x] Overwrite
- [x] Dockerize
- [ ] Collect all the datas!

### Model and Store Data

- [x] Build data storage
- [x] Model data
  - [x] Create data models for data sources
  - [x] Build logic for modeling data records
    - [x] Data source 1 scraper
      - [x] Rename '#' column to 'Season'
    - [x] Data source 2 scraper
      - [x] Rename '#' column to 'Season'
    - [x] Data source 3 scraper
      - [x] Rename 'Job' column to 'Occupation'
    - [x] Data source 4 scraper
      - [x] Rename 'Job' column to 'Occupation'
    - [x] DB class hardcoded data structures and helper methods
- [x] Build and implement helper class to insert scraped data into database

### Analysis and Conclusions

- [ ] Analyze data and draw conclusions
  - [ ] How should I handle missing data?

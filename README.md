# The Bachelor/Bachelorette Contestant Face Analysis

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
* season: Optional. Default: None. An integer associated with a desired season to collect data on. Only applicable with data sources 3 and 4.
* contestant: Optional. Default: None. A case insensitive string of the first and last name separated by a "_" of a contestant from any season of The Bachelor or Bachelorette. Only applicable with data source 5.
* output: Optional. Default: db. A case insensitive string desired output format for the collected data - either "db" for inserting the data into a SQL database or "file" for writing the data to a json file in ./data/. Applicable with all data sources.

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

Collect data from all contestants from all seasons of the Bachelor and write the data to a json file located in ./data/:
```
docker build collection/ --tag collection
docker run --volume $(pwd):/home/ collection 3 --output file
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

- [ ] Build scrapers
  - [x] Data source 1 scraper
  - [x] Data source 2 scraper
  - [x] Data source 3 scraper
  - [x] Data source 4 scraper
  - [ ] Data source 5 scraper
    - [x] Scrape photo
    - [x] Scrape personal info
    - [ ] Scrape additional personal info (i.e. height)
- [x] Multiprocess
- [ ] Options
  - [x] Seasons
  - [x] Contestants
  - [ ] Output format (this will tie-in to the "Model and Store Data" phase)
- [x] Dockerize
- [ ] Collect all the datas!

### Model and Store Data

- [ ] Build data storage
- [ ] Model data

### Analysis and Conclusions

- [ ] Analyze data and draw conclusions

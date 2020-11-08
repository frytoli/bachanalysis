# The Bachelor/Bachelorette Contestant Face Analysis

![](https://gph.is/2W1R2EC)

DSCI-510 Final Project

Compare the physical features and place (the number of episodes the contestant was on the show for) of past contestants of ABC's The Bachelor and The Bachelorette.

## How to Run

### Collection

## Data source numbers:

1. General info of all Bachelor seasons
2. General info of all Bachelorette seasons
3. General info and place of all Bachelor contestants
4. General info and place of all Bachelorette contestants
5. Photos and additional physical info of all Bachelor/Bachelorette cast members

## Arguments:

* scraper: Required. An integer associated with the desired scraper to be executed. This can be a list of integers.
* season: Optional. Default: None. An integer associated with a desired season to collect data on. Only applicable with data sources 3 and 4.
* contestant: Optional. Default: None. A case insensitive string of the first and last name separated by a "_" or "-" of a contestant from any season of The Bachelor or Bachelorette. Only applicable with data source 5.

## Examples:

Collect all available data from all sources:
```
docker build collection/ --name collection
docker run collection 1 2 3 4 5
```

Collect data from The Bachelor season 14:
```
docker build collection/ --name collection
docker run collection 3 --season 14
```

Collect data about The Bachelorette contestant Dale Moss:
```
docker build collection/ --name collection
docker run collection 5 --contestant dale_moss
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

### Model and Store Data

- [ ] Build data storage
- [ ] Model data

### Analysis and Conclusions

- [ ] Analyze data and draw conclusions

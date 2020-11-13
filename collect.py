#!/usr/bin/env python

'''
* Data collection (from remote and local sources)
* Facilitate the conversion of raw data into the data model format (json)
* Facilitate the storage of modeled data (sql database)
'''

from multiprocessing import Pool
from scrapers import *
import pandas as pd
import argparse
import random
import json
import time
import data
import db
import os
import re

# Global var for path to volume within container
PATH_TO_VOLUME = os.path.join(os.getcwd(), 'local')
# Global var for path to database
PATH_TO_DB = os.path.join(PATH_TO_VOLUME, 'thebach.db')
# Global compiled regex pattern for Wikipedia references
REF_PATTERN = re.compile(r'\[.*\]')

'''
Helper functions
'''
def remove_wikipedia_refs(raw_data):
    # Replace pairs with references with pairs without references
    for record in raw_data:
        for key, value in record.items():
            if type(value) == str and '[' in value:
                record[key] = REF_PATTERN.sub('', value)
            try:
                record[key] = int(record[key])
            except ValueError:
                # Cannot convert value to int
                pass
    return(raw_data)

'''
Data Sets 1.1 and 1.2
Collect general information from all seasons of The Bachelor or The Bachelorette
https://en.wikipedia.org/wiki/The_Bachelor_(American_TV_series)
https://en.wikipedia.org/wiki/The_Bachelorette
'''
def scrape1():
    # Initialize sqldb object
    bachdb = db.bachdb(PATH_TO_DB)
    # Initialize data model handler object
    bachdata = data.bachdata()
    # Scrape
    scraped = wikipedia.scrape('bachelor')
    time.sleep(random.uniform(3,8))
    scraped += wikipedia.scrape('bachelorette')
    # Clean Wikipedia references from key-value pairs
    scraped = remove_wikipedia_refs(scraped)
    # Model the raw data
    modeled_data = bachdata.model_many(1, scraped)
    # Add the modeled data to ds1 table
    bachdb.insert_docs('ds1', modeled_data)

'''
Data Sets 2.1 and 2.2
Collect general information about all contestants from a given season or all seasons of The Bachelor or The Bachelorette
https://bachelor-nation.fandom.com/wiki/The_Bachelor_(Season_1)
https://bachelor-nation.fandom.com/wiki/The_Bachelorette_(Season_1)
'''
def scrape2(show, season):
    # Initialize sqldb object
    bachdb = db.bachdb(PATH_TO_DB)
    # Initialize data model handler object
    bachdata = data.bachdata()
    # Assume asyncronous scraping
    time.sleep(random.uniform(3,8))
    # Scrape
    if show == 0:
        scraped = bachelornation.scrape_season('bachelor', season)
    elif show == 1:
        scraped = bachelornation.scrape_season('bachelorette', season)
    # Continue if response is not empty
    if len(scraped) > 0:
        # Model the raw data
        modeled_data = bachdata.model_many(2, scraped)
        # Add the modeled data to ds2 table
        bachdb.insert_docs('ds2', modeled_data)

'''
Data Set 3
Collect photos and additional physical information of one Bachelor/Bachelorette cast member or all Bachelor/Bachelorette cast members
https://bachelor-nation.fandom.com/wiki/Alex_Michel
'''
def scrape3(contestant):
    # Initialize sqldb object
    bachdb = db.bachdb(PATH_TO_DB)
    # Initialize data model handler object
    bachdata = data.bachdata()
    # Assume asyncronous scraping
    time.sleep(random.uniform(3,8))
    # Scrape
    scraped = bachelornation.scrape_contestant(contestant)
    # Continue if response is not empty
    if len(scraped) > 0:
        # Model the raw data
        modeled_data = bachdata.model_one(3, scraped)
        # Add the modeled data to ds3 table
        if modeled_data != {}:
            bachdb.insert_doc('ds3', modeled_data)

'''
Collection Source Handlers
'''
def getremote(ds, show, season, contestant):
    if ds == 1:
        scrape1()
    elif ds == 2:
        if season:
            scrape2(show, season)
    elif ds == 3:
        if contestant:
            scrape3(contestant)

def getlocal(ds):
    # Initialize sqldb object
    bachdb = db.bachdb(PATH_TO_DB)
    # Initialize data model handler object
    bachdata = data.bachdata()
    # Validate existence of file
    if os.path.exists(os.path.join(PATH_TO_VOLUME), f'raw{ds}.json'):
        # Read local file in from ./local/
        with open(os.path.join(PATH_TO_VOLUME, f'raw{ds}.json'), 'r') as injson:
            raw_data = json.load(injson)
        # Model the raw data
        modeled_data = bachdata.model_many(ds, scraped)
        # Add the modeled data to ds1 table
        bachdb.insert_docs(f'ds{ds}', modeled_data)
    else:
        print(f'Mayday! No input file ./local/raw{ds}.json found')

'''
Main
'''
def main():
    # Retrieve args
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('dataset', metavar='DS', type=int, nargs='+', help='an integer associated with a data set (i.e. 4)')
    parser.add_argument('--source', dest='source', type=str, nargs='+', choices=['remote','local'], default='remote', help='where to gather the data for the data set(s) (local files must be named raw{ds}.json where ds is the number associated with the data set, i.e. raw2.json)')
    parser.add_argument('--season', dest='season', type=int, nargs='+', default=[], help='an integer season (only applicable with data sources 3 and 4) (i.e. 11)')
    parser.add_argument('--contestant', dest='contestant', type=str, nargs='+', default=[], help='a string contestant first and last name separated by "_" (only applicable with data source 5) (i.e. joelle_fletcher)')
    parser.add_argument('--overwrite', dest='overwrite', action='store_true', help='overwrite applicable table(s) in the database')
    args = parser.parse_args()

    # Initialize multiprocessing pool with 5 threads
    pool = Pool(processes=5)

    # Initialize sqldb object
    bachdb = db.bachdb(PATH_TO_DB)
    # Initialize data model handler object
    bachdata = data.bachdata()

    # Drop and create new data source tables, if applicable
    if args.overwrite:
        for ds in args.dataset:
            bachdb.create_table(f'ds{ds}', bachdata.get_sql_table_values(ds), drop_existing=True)

    # If source is set to local, read data in from files located in ./local/
    if args.source == 'local':
        pool_resp = pool.map_async(getlocal, args.dataset)
        pool_resp.get()
    # Else, scrape the data from remote sources
    else:
        # Prepare params for multiprocessing
        params = []
        for ds in args.dataset:
            # Data sets 1.1 and 1.2
            if ds == 1:
                params.append((ds, None, None, None))
            # Data sets 2.1 and 2.2
            elif ds == 2:
                for show in [0, 1]:
                    seasons = []
                    # If no seasons are given by user...
                    if len(args.season) == 0:
                        # Retrieve all seasons from database
                        max_season = bachdb.get_max_val('ds1','season',filters=[{'key':'show','operator':'==','comparison':show}])
                        if max_season > 0:
                            seasons = list(range(1, max_season+1))
                        # If no data was retrieved, alert the user
                        else:
                            print('Mayday! Unable to collect data set 2. Has data set 1 been collected and stored?')
                            seaons = []
                    else:
                        seasons = args.season
                    # Iterate over seasons and append to params
                    params += [(ds, show, season, None) for season in seasons]
            # Data set 3
            elif ds == 3:
                # If no contestants are given by user...
                if len(args.contestant) == 0:
                    # Retrieve all contestants from database (note the returned value is a list of tuples)
                    contestants = [contestant[0] for contestant in bachdb.get_docs('ds2', column='profile_url')]
                    # If no data was retrieved, alert the user
                    if len(contestants) == 0:
                        print(f'Mayday! Unable to collect data set 3. Has data set 2 been collected and stored?')
                else:
                    contestants = args.contestant
                # Iterate over contestants and append to params
                params += [(ds, None, None, contestant) for contestant in contestants]
        # Let 'er rip
        pool_resp = pool.starmap_async(getremote, params)
        pool_resp.get()

if __name__ == '__main__':
    main()

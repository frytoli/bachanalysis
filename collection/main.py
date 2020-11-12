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
def remove_wikipedia_refs(data):
    # Replace pairs with references with pairs without references
    for record in data:
        for key, value in record.items():
            if type(value) == str and '[' in value:
                record[key] = REF_PATTERN.sub('', value)
            try:
                record[key] = int(record[key])
            except ValueError:
                # Cannot convert value to int
                pass
    return(data)

'''
Data Sets 1 and 2
Collect general information from all seasons of The Bachelor or The Bachelorette
https://en.wikipedia.org/wiki/The_Bachelor_(American_TV_series)
https://en.wikipedia.org/wiki/The_Bachelorette
'''
def scrape12(ds):
    # Initialize sqldb object
    bachdb = db.bachdb(PATH_TO_DB)
    # Assume the execution of multiple requests, randomize execution time
    time.sleep(random.uniform(3,8))
    if ds == 1:
        resp = wikipedia.scrape('bachelor')
    elif ds == 2:
        resp = wikipedia.scrape('bachelorette')
    else:
        print(f'Mayday! Cannot scrape data set {ds} with scraper "wikipedia"')
        return []
    # Clean Wikipedia references from key-value pairs
    resp = remove_wikipedia_refs(resp)
    # Add documents to ds1 table
    bachdb.insert_docs(f'ds{ds}', resp)

'''
Data Sets 3 and 4
Collect general information about all contestants from a given season or all seasons of The Bachelor or The Bachelorette
https://bachelor-nation.fandom.com/wiki/The_Bachelor_(Season_1)
https://bachelor-nation.fandom.com/wiki/The_Bachelorette_(Season_1)
'''
def scrape34(ds, season):
    # Initialize sqldb object
    bachdb = db.bachdb(PATH_TO_DB)
    # Assume the execution of multiple requests, randomize execution time
    time.sleep(random.uniform(3,8))
    if ds == 3:
        resp = bachelornation.scrape_season('bachelor', season)
    elif ds == 4:
        resp = bachelornation.scrape_season('bachelorette', season)
    else:
        print(f'Mayday! Cannot scrape data set {ds} with scraper "bacahelornation"')
        return []
    # Continue if response is not empty
    if len(resp) > 0:
        # Add documents to ds3 table
        bachdb.insert_docs(f'ds{ds}', resp)

'''
Data Set 5
Collect photos and additional physical information of one Bachelor/Bachelorette cast member or all Bachelor/Bachelorette cast members
https://bachelor-nation.fandom.com/wiki/Alex_Michel
'''
def scrape5(contestant):
    # Initialize sqldb object
    bachdb = db.bachdb(PATH_TO_DB)
    # Assume the execution of multiple requests, randomize execution time
    time.sleep(random.uniform(3,8))
    resp = bachelornation.scrape_contestant(contestant)
    # Continue if response is not empty
    if len(resp) > 0:
        # Add documents to ds5 table
        bachdb.insert_doc('ds5', resp)

def getremote(ds, season, contestant):
    if ds == 1 or ds == 2:
        resp = scrape12(ds)
    elif ds == 3 or ds == 4:
        if season:
            scrape34(ds, season)
    elif ds == 5:
        if contestant:
            scrape5(contestant)

def getlocal(ds):
    # Initialize sqldb object
    bachdb = db.bachdb(PATH_TO_DB)
    # Validate existence of file
    if os.path.exists(os.path.join(PATH_TO_VOLUME), f'raw{ds}.json'):
        # Read local file in from ./local/
        with open(os.path.join(PATH_TO_VOLUME, f'raw{ds}.json'), 'r') as injson:
            data = json.load(injson)
        # Add documents in batch to database
        bachdb.insert_docs(f'ds{ds}', data)
    else:
        print(f'Mayday! No input file ./local/raw{ds}.json found')

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

    # Drop and create new data source tables, if applicable
    if args.overwrite:
        for dataset in args.dataset:
            bachdb.create_table(f'ds{dataset}', drop_existing=True)

    # If source is set to local, read data in from files located in ./local/
    if args.source == 'local':
        pool_resp = pool.map_async(getlocal, args.dataset)
        pool_resp.get()
    # Else, scrape the data from remote sources
    else:
        # Prepare params for multiprocessing
        params = []
        for ds in args.dataset:
            # Data sets 1 and 2
            if ds == 1 or ds == 2:
                params.append((ds, None, None))
            # Data sets 3 and 4
            elif ds == 3 or ds == 4:
                # If no seasons are given by user...
                if len(args.season) == 0:
                    # Retrieve all seasons from database
                    max_season = bachdb.get_max_val(f'ds{ds-2}','season')
                    if max_season > 0:
                        seasons = list(range(1, max_season+1))
                    # If no data was retrieved, alert the user
                    else:
                        print(f'Mayday! Unable to collect data set {ds}. Has data set {ds-2} been collected and stored?')
                        seaons = []
                else:
                    seasons = args.season
                # Iterate over seasons and append to params
                params += [(ds, season, None) for season in seasons]
            # Data set 5
            elif ds == 5:
                # If no contestants are given by user...
                if len(args.contestant) == 0:
                    # Retrieve all contestants from database
                    contestants = []
                    contestants += bachdb.get_docs('ds3', column='profile_url')
                    contestants += bachdb.get_docs('ds4', column='profile_url')
                    # If no data was retrieved, alert the user
                    if len(contestants) == 0:
                        print(f'Mayday! Unable to collect data set 5. Have data sets 3 or 4 been collected and stored?')
                else:
                    contestants = args.contestant
                # Iterate over contestants and append to params
                params += [(ds, None, contestant) for contestant in contestants]
        # Let 'er rip
        pool_resp = pool.starmap_async(getremote, params)
        pool_resp.get()

if __name__ == '__main__':
    main()

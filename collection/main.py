#!/usr/bin/env python

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
PATH_TO_VOLUME = os.path.join(os.getcwd(), 'data')
# Global var for path to database
PATH_TO_DB = os.path.join(PATH_TO_VOLUME, 'thebach.db')
# Global compiled regex pattern for Wikipedia references
REF_PATTERN = re.compile(r'\[.*\]')

'''
Helper functions
'''
def save_to_file(data, ds):
    # Write json response to file
    with open(os.path.join(PATH_TO_VOLUME, f'{ds}.json'),'w') as outfile:
        json.dump(data, outfile, indent=2)

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
Collect general information from all seasons of The Bachelor
https://en.wikipedia.org/wiki/The_Bachelor_(American_TV_series)
'''
def scrape1(_):
    # Initialize sqldb object
    bachdb = db.bachdb(PATH_TO_DB)
    # Assume the execution of multiple requests, randomize execution time
    time.sleep(random.uniform(3,8))
    resp = wikipedia.scrape('bachelor')
    # Clean Wikipedia references from key-value pairs
    resp = remove_wikipedia_refs(resp)
    # Add documents to ds1 table
    bachdb.insert_docs('ds1', resp)
    return resp

'''
Collect general information from all seasons of The Bachelorette
https://en.wikipedia.org/wiki/The_Bachelorette
'''
def scrape2(_):
    # Initialize sqldb object
    bachdb = db.bachdb(PATH_TO_DB)
    # Assume the execution of multiple requests, randomize execution time
    time.sleep(random.uniform(3,8))
    resp = wikipedia.scrape('bachelorette')
    # Clean Wikipedia references from key-value pairs
    resp = remove_wikipedia_refs(resp)
    # Add documents to ds2 table
    bachdb.insert_docs('ds2', resp)
    return resp

'''
Collect general information about all contestants from a given season or all seasons of The Bachelor
https://bachelor-nation.fandom.com/wiki/The_Bachelor_(Season_1)
'''
def scrape3(season):
    # Initialize sqldb object
    bachdb = db.bachdb(PATH_TO_DB)
    # Assume the execution of multiple requests, randomize execution time
    time.sleep(random.uniform(3,8))
    resp = bachelornation.scrape_season('bachelor', season)
    # Continue if response is not empty
    if len(resp) > 0:
        # Add documents to ds3 table
        bachdb.insert_docs('ds3', resp)
    return resp

'''
Collect general information about all contestants from a given season or all seasons of The Bachelorette
https://bachelor-nation.fandom.com/wiki/The_Bachelorette_(Season_1)
'''
def scrape4(season):
    # Initialize sqldb object
    bachdb = db.bachdb(PATH_TO_DB)
    # Assume the execution of multiple requests, randomize execution time
    time.sleep(random.uniform(3,8))
    resp = bachelornation.scrape_season('bachelorette', season)
    # Continue if response is not empty
    if len(resp) > 0:
        # Add documents to ds4 table
        bachdb.insert_docs('ds4', resp)
    return resp

'''
Collect photos and additional physical information of one Bachelor/Bachelorette cast member or all Bachelor/Bachelorette cast members
https://bachelor-nation.fandom.com/wiki/Alex_Michel
'''
def scrape5(profile_url):
    # Initialize sqldb object
    bachdb = db.bachdb(PATH_TO_DB)
    # Assume the execution of multiple requests, randomize execution time
    time.sleep(random.uniform(3,8))
    resp = bachelornation.scrape_contestant(profile_url)
    # Continue if response is not empty
    if len(resp) > 0:
        # Add documents to ds5 table
        bachdb.insert_doc('ds5', resp)
    del resp # Do this better (handle file output option)
    #return resp

def main():
    # Retrieve args
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('scraper', metavar='N', type=int, nargs='+', help='an integer associated with a data source (i.e. 4)')
    parser.add_argument('--season', dest='season', type=int, nargs='+', default=[], help='an integer season (only applicable with data sources 3 and 4) (i.e. 11)')
    parser.add_argument('--contestant', dest='contestant', type=str, nargs='+', default=[], help='a string contestant first and last name separated by "_" (only applicable with data source 5) (i.e. joelle_fletcher)')
    parser.add_argument('--file', dest='file', action='store_true', help='write output data to a file')
    parser.add_argument('--overwrite', dest='overwrite', action='store_true', help='overwrite applicable table(s) in the database')
    args = parser.parse_args()

    # Initialize sqldb object
    bachdb = db.bachdb(PATH_TO_DB)

    # Initialize multiprocessing pool with 5 threads
    pool = Pool(processes=5)
    # Run asyncronous processes
    if 1 in args.scraper:
        # Drop and create a new ds1 table, if applicable
        if args.overwrite:
            bachdb.create_table('ds1', drop_existing=True)
        ds1_data = pool.map_async(scrape1, [None])
        ds1_resp = ds1_data.get()
        # If applicable, write data to file
        if args.file:
            ds1_out = pool.starmap_async(save_to_file, [[ds1_resp, 'ds1']])
            ds1_out.get()
    if 2 in args.scraper:
        # Drop and create a new ds2 table, if applicable
        if args.overwrite:
            bachdb.create_table('ds2', drop_existing=True)
        ds2_data = pool.map_async(scrape2, [None])
        ds2_resp = ds2_data.get()
        # If applicable, write data to file
        if args.file:
            ds2_out = pool.starmap_async(save_to_file, [[ds2_resp, 'ds2']])
            ds2_out.get()
    if 3 in args.scraper:
        # Drop and create a new ds3 table, if applicable
        if args.overwrite:
            bachdb.create_table('ds3', drop_existing=True)
        # If seasons were input, continue with the seasons
        if len(args.season) > 0:
            seasons = args.season
        # Else, read seasons from database
        else:
            max_season = bachdb.get_max_val('ds1','season')
        if max_season > 0:
            seasons = list(range(1, max_season+1))
            ds3_data = pool.map_async(scrape3, seasons)
            ds3_resp = ds3_data.get()
            # If applicable, write data to file
            if args.file:
                ds3_out = pool.starmap_async(save_to_file, [[ds3_resp, 'ds3']])
                ds3_out.get()
    if 4 in args.scraper:
        # Drop and create a new ds4 table, if applicable
        if args.overwrite:
            bachdb.create_table('ds4', drop_existing=True)
        # If seasons were input, continue with the seasons
        if len(args.season) > 0:
            seasons = args.season
        # Else, read seasons from database
        else:
            max_season = bachdb.get_max_val('ds2','season')
        if max_season > 0:
            seasons = list(range(1, max_season+1))
            ds4_data = pool.map_async(scrape4, seasons)
            ds4_resp = ds4_data.get()
            # If applicable, write data to file
            if args.file:
                ds4_out = pool.starmap_async(save_to_file, [[ds4_resp, 'ds4']])
                ds4_out.get()
    if 5 in args.scraper:
        # Drop and create a new ds5 table, if applicable
        if args.overwrite:
            bachdb.create_table('ds5', drop_existing=True)
        # If seasons were input, continue with the seasons
        if len(args.contestant) > 0:
            contestants = args.contestant
        # Else, read contestants from database
        else:
            profile_urls = []
            profile_urls += bachdb.get_docs('ds3', column='profile_url')
            profile_urls += bachdb.get_docs('ds4', column='profile_url')
        if len(profile_urls) > 0:
            ds5_data = pool.map_async(scrape5, [profile_url[0] for profile_url in profile_urls]) # Account for the fact that sqlite3 returns tuples
            ds5_resp = ds5_data.get()
            # If applicable, write data to file
            if args.file:
                ds5_out = pool.starmap_async(save_to_file, [[ds5_resp, 'ds5']])
                ds5_out.get()


if __name__ == '__main__':
    main()

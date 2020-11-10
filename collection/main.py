#!/usr/bin/env python

from multiprocessing import Pool
from scrapers import *
import pandas as pd
import argparse
import random
import sqldb
import json
import time
import os
import re

# Global var for path to volume within container
PATH_TO_VOLUME = os.path.join(os.getcwd(), 'data')
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

def flatten_data(data):
    # Flatten the nested response and do not store Nonetype objects
    flat_data = []
    for resp in data:
        if resp:
            flat_data += resp
    return flat_data

'''
Collect general information from all seasons of The Bachelor
https://en.wikipedia.org/wiki/The_Bachelor_(American_TV_series)
'''
def scrape1(_):
    # Assume the execution of multiple requests, randomize execution time
    time.sleep(random.uniform(3,8))
    resp = ds1.scrape()
    # Clean Wikipedia references from key-value pairs
    resp = remove_wikipedia_refs(resp)
    return resp

'''
Collect general information from all seasons of The Bachelorette
https://en.wikipedia.org/wiki/The_Bachelorette
'''
def scrape2(_):
    # Assume the execution of multiple requests, randomize execution time
    time.sleep(random.uniform(3,8))
    resp = ds2.scrape()
    # Clean Wikipedia references from key-value pairs
    resp = remove_wikipedia_refs(resp)
    return resp

'''
Collect general information about all contestants from a given season or all seasons of The Bachelor
https://en.wikipedia.org/wiki/The_Bachelor_(season_1)
'''
def scrape3(season):
    # Assume the execution of multiple requests, randomize execution time
    time.sleep(random.uniform(3,8))
    resp = ds3.scrape_season(season)
    # Clean Wikipedia references from key-value pairs
    if resp:
        resp = remove_wikipedia_refs(resp)
    return resp

'''
Collect general information about all contestants from a given season or all seasons of The Bachelorette
https://en.wikipedia.org/wiki/The_Bachelorette_(season_1)
'''
def scrape4(season):
    # Assume the execution of multiple requests, randomize execution time
    time.sleep(random.uniform(3,8))
    resp = ds4.scrape_season(season)
    # Clean Wikipedia references from key-value pairs
    if resp:
        resp = remove_wikipedia_refs(resp)
    return resp

'''
Collect photos and additional physical information of one Bachelor/Bachelorette cast member or all Bachelor/Bachelorette cast members
https://bachelor-nation.fandom.com/wiki/Alex_Michel
'''
def scrape5(contestant):
    # Assume the execution of multiple requests, randomize execution time
    time.sleep(random.uniform(3,8))
    resp = ds5.scrape_contestant(contestant)
    return resp

def main():
    # Retrieve args
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('scraper', metavar='N', type=int, nargs='+', help='an integer associated with a data source (i.e. 4)')
    parser.add_argument('--season', dest='season', type=int, nargs='+', default=[None], help='an integer season (only applicable with data sources 3 and 4) (i.e. 11)')
    parser.add_argument('--contestant', dest='contestant', type=str, nargs='+', default=[None], help='a string contestant first and last name separated by "_" (only applicable with data source 5) (i.e. joelle_fletcher)')
    parser.add_argument('--output', dest='output', type=str, choices=['db', 'file'], default='db', help='a string desired output format for collected data: (db or file)')
    args = parser.parse_args()

    # Specify output format
    output_format = args.output.lower()

    # Initialize sqldb object
    db = sqldb.db(os.path.join(PATH_TO_VOLUME, 'bach.db'))

    # Initialize multiprocessing pool with 5 threads
    pool = Pool(processes=5)
    # Run asyncronous processes
    if 1 in args.scraper:
        ds1_data = pool.map_async(scrape1, [None])
        ds1_resp = ds1_data.get()
        # Flatten nested mp response
        ds1_flat = flatten_data(ds1_resp)
        # Write flattened json response to file, if applicable
        if output_format == 'file':
            ds1_out = pool.starmap_async(save_to_file, [[ds1_flat, 'ds1']])
            ds1_out.get()
        # Else, insert documents into database
        else:
            # Create a ds1 table (drop previously existing if applicable)
            db.create_table('ds1', db.craft_headers(ds1_flat[0]), drop_existing=True)
            # Add documents to ds1 table
            db.insert_docs('ds1', ds1_flat)
    if 2 in args.scraper:
        ds2_data = pool.map_async(scrape2, [None])
        ds2_resp = ds2_data.get()
        # Flatten nested mp response
        ds2_flat = flatten_data(ds2_resp)
        # Write flattened json response to file, if applicable
        if output_format == 'file':
            ds2_out = pool.starmap_async(save_to_file, [[ds2_flat, 'ds2']])
            ds2_out.get()
        # Else, insert documents into database
        else:
            # Create a ds2 table (drop previously existing if applicable)
            db.create_table('ds2',  db.craft_headers(ds2_flat[0]), drop_existing=True)
            # Add documents to ds2 table
            db.insert_docs('ds2', ds2_flat)
    if 3 in args.scraper:
        if args.season == [None]:
            # Attempt to read data from database
            max_season = db.get_max_val('ds1','season')
            # Otherwise, attempt to read data from data source 1 json file
            if max_season == 0:
                if os.path.exists(os.path.join(PATH_TO_VOLUME, 'ds1.json')):
                    with open(os.path.join(PATH_TO_VOLUME, 'ds1.json'),'r') as injson:
                        general_info = json.load(injson)
                    max_season = max([rec['season'] for rec in general_info])
                else:
                    print('No source for The Bachelor seasons. Please run collection on data source 1. Skipping.')
        else:
            seasons = args.season
        if max_season > 0:
            seasons = list(range(1, max_season+1))
            ds3_data = pool.map_async(scrape3, seasons)
            ds3_resp = ds3_data.get()
            # Flatten nested mp response
            ds3_flat = flatten_data(ds3_resp)
            # Write json response to file, if applicable
            if output_format == 'file':
                # Do not store Nonetype objects and flatten nested data
                ds3_out = pool.starmap_async(save_to_file, [[ds3_flat, 'ds3']])
                ds3_out.get()
            # Else, insert documents into database
            else:
                # Create a ds3 table (drop previously existing if applicable)
                db.create_table('ds3',  db.craft_headers(ds3_flat[0]), drop_existing=True)
                # Add documents to ds3 table
                db.insert_docs('ds3', ds3_flat)
    if 4 in args.scraper:
        if args.season == [None]:
            # Attempt to read data from database
            max_season = db.get_max_val('ds2','season')
            # Otherwise, attempt to read data from data source 2 json file
            if max_season == 0:
                if os.path.exists(os.path.join(PATH_TO_VOLUME, 'ds2.json')):
                    with open(os.path.join(PATH_TO_VOLUME, 'ds2.json'),'r') as injson:
                        general_info = json.load(injson)
                    max_season = max([rec['season'] for rec in general_info])
                else:
                    print('No source for The Bachelorette seasons. Please run collection on data source 2. Skipping.')
        else:
            seasons = args.season
        if max_season > 0:
            seasons = list(range(1, max_season+1))
            ds4_data = pool.map_async(scrape4, seasons)
            ds4_resp = ds4_data.get()
            # Flatten nested mp response
            ds4_flat = flatten_data(ds4_resp)
            # Write json response to file, if applicable
            if output_format == 'file':
                # Do not store Nonetype objects and flatten nested data
                ds4_out = pool.starmap_async(save_to_file, [[ds4_flat, 'ds4']])
                ds4_out.get()
            # Else, insert documents into database
            else:
                # Create a ds3 table (drop previously existing if applicable)
                db.create_table('ds4',  db.craft_headers(ds4_flat[0]), drop_existing=True)
                # Add documents to ds3 table
                db.insert_docs('ds4', ds4_flat)
    if 5 in args.scraper:
        if args.contestant == [None]:
            # Read-in json files of all previously collected contestants
            contestants = []
            # Attempt to read data from database
            contestants += db.get_docs('ds3')
            contestants += db.get_docs('ds4')
            # Otherwise, attempt to read data from data sources 3 and 4 files
            if contestants == []:
                # Bachelor contestants
                if os.path.exists(os.path.join(PATH_TO_VOLUME, 'ds3.json')):
                    df = pd.read_json(os.path.join(PATH_TO_VOLUME, 'ds3.json'))
                    contestants += [name.strip().replace(' ','_') for name in df['Name']]
                else:
                    print('No source for The Bachelor contestants. Please run collection on data source 3. Skipping.')
                # Bachelorette contestants
                if os.path.exists(os.path.join(PATH_TO_VOLUME, 'ds4.json')):
                    df = pd.read_json(os.path.join(PATH_TO_VOLUME, 'ds4.json'))
                    contestants += [name.strip().replace(' ','_') for name in df['Name']]
                else:
                    print('No source for The Bachelorette contestants. Please run collection on data source 4. Skipping.')
        else:
            contestants = args.contestant
        if contestants != []:
            ds5_data = pool.map_async(scrape5, contestants)
            ds5_resp = ds5_data.get()
            # Write json response to file, if applicable
            if output_format == 'file':
                # Do not store Nonetype objects and flatten nested data
                ds5_out = pool.starmap_async(save_to_file, [[ds5_resp, 'ds5']])
                ds5_out.get()
            # Else, insert documents into database
            else:
                # Do not store Nonetype objects
                ds5_good = [doc for doc in ds5_resp if doc]
                if ds5_good != []:
                    # Create a ds3 table (drop previously existing if applicable)
                    db.create_table('ds5',  db.craft_headers(ds5_good[0]), drop_existing=True)
                    # Add documents to ds3 table
                    db.insert_docs('ds5', [doc for doc in ds5_good if doc])


if __name__ == '__main__':
    main()

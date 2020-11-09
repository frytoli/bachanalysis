#!/usr/bin/env python

from multiprocessing import Pool
from scrapers import *
import pandas as pd
import argparse
import random
import json
import time
import os

# Global vars for current Bachelor/Bachelorette season count
MAX_BACHELOR_SEASON = 24
MAX_BACHELORETTE_SEASON = 16

'''
Collect general information from all seasons of The Bachelor
https://en.wikipedia.org/wiki/The_Bachelor_(American_TV_series)
'''
def scrape1(to_db=True):
    # Assume the execution of multiple requests, randomize execution time
    time.sleep(random.uniform(3,8))
    resp = ds1.scrape()
    return resp

'''
Collect general information from all seasons of The Bachelorette
https://en.wikipedia.org/wiki/The_Bachelorette
'''
def scrape2(to_db=True):
    # Assume the execution of multiple requests, randomize execution time
    time.sleep(random.uniform(3,8))
    resp = ds2.scrape()
    return resp

'''
Collect general information about all contestants from a given season or all seasons of The Bachelor
https://en.wikipedia.org/wiki/The_Bachelor_(season_1)
'''
def scrape3(season, to_db=True):
    # Assume the execution of multiple requests, randomize execution time
    time.sleep(random.uniform(3,8))
    resp = ds3.scrape_season(season)
    return resp

'''
Collect general information about all contestants from a given season or all seasons of The Bachelorette
https://en.wikipedia.org/wiki/The_Bachelorette_(season_1)
'''
def scrape4(season, to_db=True):
    # Assume the execution of multiple requests, randomize execution time
    time.sleep(random.uniform(3,8))
    resp = ds4.scrape_season(season)
    return resp

'''
Collect photos and additional physical information of one Bachelor/Bachelorette cast member or all Bachelor/Bachelorette cast members
https://bachelor-nation.fandom.com/wiki/Alex_Michel
'''
def scrape5(contestant, to_db=True):
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
    to_db = True
    if args.output.lower() == 'file':
        to_db = False
        path_to_volume = os.path.join(os.getcwd(), 'data')

    # Initialize multiprocessing pool with 5 threads
    pool = Pool(processes=5)
    # Run asyncronous processes
    if 1 in args.scraper:
        ds1_data = pool.apply_async(scrape1, kwds={'to_db':to_db})
        ds1_resp = ds1_data.get()
        # Write json response to file, if applicable
        if not to_db:
            with open(os.path.join(path_to_volume, 'ds1.json'),'w') as outfile:
                json.dump(ds1_resp, outfile, indent=2)
    if 2 in args.scraper:
        ds2_data = pool.apply_async(scrape2, kwds={'to_db':to_db})
        ds2_resp = ds2_data.get()
        # Write json response to file, if applicable
        if not to_db:
            with open(os.path.join(path_to_volume, 'ds2.json'),'w') as outfile:
                json.dump(ds2_resp, outfile, indent=2)
    if 3 in args.scraper:
        if args.season == [None]:
            seasons = list(range(1, MAX_BACHELOR_SEASON+1)) # Hardcoded max episodes
        else:
            seasons = args.season
        ds3_data = pool.apply_async(scrape3, seasons, kwds={'to_db':to_db for s in seasons})
        ds3_resp = ds3_data.get()
        # Write json response to file, if applicable
        if not to_db:
            with open(os.path.join(path_to_volume, 'ds3.json'),'w') as outfile:
                json.dump(ds3_resp, outfile, indent=2)
    if 4 in args.scraper:
        if args.season == [None]:
            seasons = list(range(1, MAX_BACHELORETTE_SEASON+1)) # Hardcoded max episodes
        else:
            seasons = args.season
        ds4_data = pool.apply_async(scrape4, seasons, kwds={'to_db':to_db for s in seasons})
        ds4_resp = ds4_data.get()
        # Write json response to file, if applicable
        if not to_db:
            with open(os.path.join(path_to_volume, 'ds4.json'),'w') as outfile:
                json.dump(ds4_resp, outfile, indent=2)
    if 5 in args.scraper:
        if args.contestant == [None]:
            # Read-in json files of all previously collected contestants
            contestants = []
            # Bachelor contestants
            if os.path.exists(os.path.join(path_to_volume, 'd3.json')):
                df = pd.read_json(os.path.join(path_to_volume, 'd3.json'))
                contestants += [name.strip().replace(' ','_') for name in df['Name'] if ' ' in name.strip()]
            else:
                print('No source for Bachelor contestants. Please run collection on data source 3. Skipping.')
            # Bachelorette contestants
            if os.path.exists(os.path.join(path_to_volume, 'd4.json')):
                df = pd.read_json(os.path.join(path_to_volume, 'd4.json'))
                contestants += [name.strip().replace(' ','_') for name in df['Name'] if ' ' in name.strip()]
            else:
                print('No source for Bachelorette contestants. Please run collection on data source 4. Skipping.')
        else:
            contestants = args.contestant
        ds5_data = pool.apply_async(scrape5, contestants, kwds={'to_db':to_db for c in contestants})
        ds5_resp = ds5_data.get()
        # Write json response to file, if applicable
        if not to_db:
            with open(os.path.join(path_to_volume, 'ds5.json'),'w') as outfile:
                # Do not store Nonetype objects
                json.dump([resp for resp in ds5_data.get() if resp], outfile, indent=2)


if __name__ == '__main__':
    main()

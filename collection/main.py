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
# Global var for path to volume within container
PATH_TO_VOLUME = os.path.join(os.getcwd(), 'data')

def save_to_file(data, ds):
    # Write json response to file
    with open(os.path.join(PATH_TO_VOLUME, f'{ds}.json'),'w') as outfile:
        json.dump(data, outfile, indent=2)

'''
Collect general information from all seasons of The Bachelor
https://en.wikipedia.org/wiki/The_Bachelor_(American_TV_series)
'''
def scrape1(output_format):
    # Assume the execution of multiple requests, randomize execution time
    time.sleep(random.uniform(3,8))
    resp = ds1.scrape()
    # Write json response to file, if applicable
    if output_format == 'file':
        save_to_file(resp, 'ds1')

'''
Collect general information from all seasons of The Bachelorette
https://en.wikipedia.org/wiki/The_Bachelorette
'''
def scrape2(output_format):
    # Assume the execution of multiple requests, randomize execution time
    time.sleep(random.uniform(3,8))
    resp = ds2.scrape()
    # Write json response to file, if applicable
    if output_format == 'file':
        save_to_file(resp, 'ds2')

'''
Collect general information about all contestants from a given season or all seasons of The Bachelor
https://en.wikipedia.org/wiki/The_Bachelor_(season_1)
'''
def scrape3(season, output_format):
    # Assume the execution of multiple requests, randomize execution time
    time.sleep(random.uniform(3,8))
    resp = ds3.scrape_season(season)
    # Write json response to file, if applicable
    if output_format == 'file':
        save_to_file(resp, 'ds3')

'''
Collect general information about all contestants from a given season or all seasons of The Bachelorette
https://en.wikipedia.org/wiki/The_Bachelorette_(season_1)
'''
def scrape4(season, output_format):
    # Assume the execution of multiple requests, randomize execution time
    time.sleep(random.uniform(3,8))
    resp = ds4.scrape_season(season)
    if output_format == 'file':
        save_to_file(resp, 'ds4')

'''
Collect photos and additional physical information of one Bachelor/Bachelorette cast member or all Bachelor/Bachelorette cast members
https://bachelor-nation.fandom.com/wiki/Alex_Michel
'''
def scrape5(contestant, output_format):
    # Assume the execution of multiple requests, randomize execution time
    time.sleep(random.uniform(3,8))
    resp = ds5.scrape_contestant(contestant)
    # Write json response to file, if applicable
    if output_format == 'file':
        # Do not store Nonetype objects
        save_to_file([rec for rec in resp.get() if rec], 'ds4')

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

    # Initialize multiprocessing pool with 5 threads
    pool = Pool(processes=5)
    # Run asyncronous processes
    if 1 in args.scraper:
        ds1_data = pool.map_async(scrape1, [output_format])
        ds1_data.get()
    if 2 in args.scraper:
        ds2_data = pool.map_async(scrape2, [output_format])
        ds2_data.get()
    if 3 in args.scraper:
        if args.season == [None]:
            seasons = list(range(1, MAX_BACHELOR_SEASON+1)) # Hardcoded max episodes
        else:
            seasons = args.season
        ds3_data = pool.map_async(scrape3, [(s, output_format) for s in seasons])
        ds3_data.get()
    if 4 in args.scraper:
        if args.season == [None]:
            seasons = list(range(1, MAX_BACHELORETTE_SEASON+1)) # Hardcoded max episodes
        else:
            seasons = args.season
        ds4_data = pool.map_async(scrape4, [(s, output_format) for s in seasons])
        ds4_data.get()
    if 5 in args.scraper:
        if args.contestant == [None]:
            # Read-in json files of all previously collected contestants
            contestants = []
            # Bachelor contestants
            if os.path.exists(os.path.join(PATH_TO_VOLUME, 'd3.json')):
                df = pd.read_json(os.path.join(PATH_TO_VOLUME, 'd3.json'))
                contestants += [name.strip().replace(' ','_') for name in df['Name'] if ' ' in name.strip()]
            else:
                print('No source for Bachelor contestants. Please run collection on data source 3. Skipping.')
            # Bachelorette contestants
            if os.path.exists(os.path.join(PATH_TO_VOLUME, 'd4.json')):
                df = pd.read_json(os.path.join(PATH_TO_VOLUME, 'd4.json'))
                contestants += [name.strip().replace(' ','_') for name in df['Name'] if ' ' in name.strip()]
            else:
                print('No source for Bachelorette contestants. Please run collection on data source 4. Skipping.')
        else:
            contestants = args.contestant
        ds5_data = pool.map_async(scrape5, [(c, output_format) for c in contestants])
        ds5_data.get()


if __name__ == '__main__':
    main()

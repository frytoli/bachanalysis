#!/usr/local/bin/python3

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
MAX_BACHELORETTE_SEASON = 17

'''
Collect general information from all seasons of The Bachelor
https://en.wikipedia.org/wiki/The_Bachelor_(American_TV_series)
'''
def scrape1():
    resp = ds1.scrape()
    # Temp write data to file
    with open('../data/ds1.json','w') as outjson:
        outjson.write(resp, outjson, indent=2)
    # Assume the execution of multiple requests
    time.sleep(random.uniform(3,8))
    return resp

'''
Collect general information from all seasons of The Bachelorette
https://en.wikipedia.org/wiki/The_Bachelorette
'''
def scrape2():
    resp = ds2.scrape()
    # Temp write data to file
    with open('../data/ds2.json','w') as outjson:
        json.dump(resp, outjson, indent=2)
    # Assume the execution of multiple requests
    time.sleep(random.uniform(3,8))
    return resp

'''
Collect general information about all contestants from a given season or all seasons of The Bachelor
https://en.wikipedia.org/wiki/The_Bachelor_(season_1)
'''
def scrape3(season):
    resp = ds3.scrape_season(season)
    # Temp write data to file
    with open(f'../data/bachelor{season}.json','w') as outjson:
        json.dump(resp, outjson, indent=2)
    # Assume the execution of multiple requests
    time.sleep(random.uniform(3,8))
    return resp

'''
Collect general information about all contestants from a given season or all seasons of The Bachelorette
https://en.wikipedia.org/wiki/The_Bachelorette_(season_1)
'''
def srcape4(season):
    resp = ds4.scrape_season(season)
    with open(f'../data/bachelorette{season}.json','w') as outjson:
        json.dump(resp, outjson, indent=2)
    # Assume the execution of multiple requests
    time.sleep(random.uniform(3,8))
    return resp

'''
Collect photos and additional physical information of one Bachelor/Bachelorette cast member or all Bachelor/Bachelorette cast members
https://bachelor-nation.fandom.com/wiki/Alex_Michel
'''
def scrape5(contestant):
    resp = ds5.scrape_contestant(contestant)
    with open(f'../data/{contestant.lower()}.json','w') as outjson:
        json.dump(resp, outjson, indent=2)
    # Assume the execution of multiple requests
    time.sleep(random.uniform(3,8))
    return resp

def main():
    # Retrieve args
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('scraper', metavar='N', type=int, nargs='+', help='an integer associated with a data source (i.e. 4)')
    parser.add_argument('--season', dest='season', type=int, nargs='+', action='store', default=[None], help='an integer season (only applicable with data sources 3 and 4) (i.e. 11)')
    parser.add_argument('--contestant', dest='contestant', type=str, nargs='+', action='store', default=[None], help='a string contestant first and last name separated by "_" (only applicable with data source 5) (i.e. joelle_fletcher)')
    args = parser.parse_args()

    # Initialize multiprocessing pool with 5 threads
    pool = Pool(processes=5)
    # Run asyncronous processes
    if 1 in args.scraper:
        ds1_resp = pool.map_async(scrape1)
    if 2 in args.scraper:
        ds2_resp = pool.map_async(scrape2)
    if 3 in args.scraper:
        if args.season == [None]:
            args.season = list(range(1, MAX_BACHELOR_SEASON+1)) # Hardcoded max episodes
        ds3_resp = pool.map_async(scrape3, args.season)
    if 4 in args.scraper:
        if args.season == [None]:
            args.season = list(range(1, MAX_BACHELORETTE_SEASON+1)) # Hardcoded max episodes
        ds4_resp = pool.map_async(scrape4, args.season)
    if 5 in args.scraper:
        if args.contestant == [None]:
            # Read-in json files of all previously collected contestants
            contestants = []
            # Bachelor contestants
            for season in range(1, MAX_BACHELOR_SEASON+1): # Hardcoded max episodes
                if os.path.exists(f'../data/bachelor{season}.json'):
                    df = pd.read_json(f'../data/bachelor{season}.json')
                    contestants += [name.strip().replace(' ','_') for name in df['Name'] if ' ' in name.strip()]
            # Bachelorette contestants
            for season in range(1, MAX_BACHELORETTE_SEASON+1): # Hardcoded max episodes
                if os.path.exists(f'../data/bachelorette{season}.json'):
                    df = pd.read_json(f'../data/bachelorette{season}.json')
                    contestants += [name.strip().replace(' ','_') for name in df['Name'] if ' ' in name.strip()]
            args.contestant = contestants
        ds5_resp = pool.map_async(scrape5, args.contestant)


if __name__ == '__main__':
    main()

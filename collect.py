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
import os
import re

# Global var for path to volume within container
PATH_TO_VOLUME = os.path.join(os.getcwd(), 'local')

'''
Scrape data Sets 1.1 and 1.2
Collect general information from all seasons of The Bachelor or The Bachelorette
https://en.wikipedia.org/wiki/The_Bachelor_(American_TV_series)
https://en.wikipedia.org/wiki/The_Bachelorette
'''
def scrape1():
    # Initialize data model handler object
    bachdata = data.bachdata()
    # Scrape
    scraped = wikipedia.scrape('bachelor')
    time.sleep(random.uniform(3,8))
    scraped += wikipedia.scrape('bachelorette')
    # Model the raw data
    modeled_data = bachdata.model_many(1, scraped)
    # Return modeled json data
    return modeled_data

'''
Scrape data Sets 2.1 and 2.2
Collect general information about all contestants from a given season or all seasons of The Bachelor or The Bachelorette
https://bachelor-nation.fandom.com/wiki/The_Bachelor_(Season_1)
https://bachelor-nation.fandom.com/wiki/The_Bachelorette_(Season_1)
'''
def scrape2(show, season):
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
        # Return modeled json data
        return modeled_data

'''
Scrape data Set 3
Collect photos and additional physical information of one Bachelor/Bachelorette cast member or all Bachelor/Bachelorette cast members
https://bachelor-nation.fandom.com/wiki/Alex_Michel
'''
def scrape3(id, contestant):
    # Initialize data model handler object
    bachdata = data.bachdata()
    # Assume asyncronous scraping
    time.sleep(random.uniform(3,8))
    # Scrape
    scraped = bachelornation.scrape_contestant(contestant)
    # Continue if response is not empty
    if len(scraped) > 0:
        # Add id to raw record
        scraped['id'] = id
        # Add profile_url to record
        scraped['profile_url'] = contestant
        # Model the raw data
        modeled_data = bachdata.model_one(3, scraped)
        # Return modeled json data
        return modeled_data

'''
Data set from local file
'''
def set_ds3_ids(df2, df3):
    # Get profile_urls of all documents for which to set ids
    profile_urls = list(df3['profile_url'])
    for url in profile_urls:
        # Find record in data set 2 that corresponds to the given profile url and get the corresponding id
        id = df2.loc[df2['profile_url']==url]['id']
        # Update the associated record in data set 3
        df3.loc[df3['profile_url'] == url, ['id']] = id
    return df3

def getlocal(ds):
    # Initialize data model handler object
    bachdata = data.bachdata()
    # Validate existence of file
    if os.path.exists(os.path.join(PATH_TO_VOLUME, f'raw{ds}.json')):
        # Read local file in from ./local/
        with open(os.path.join(PATH_TO_VOLUME, f'raw{ds}.json'), 'r') as injson:
            raw_data = json.load(injson)
        # Model the raw data
        modeled_data = bachdata.model_many(ds, raw_data)
        # Convert the modeled data to pandas df and returm
        return pd.DataFrame(modeled_data)
    else:
        print(f'Mayday! No input file ./local/raw{ds}.json found')

'''
Main
'''
def main():
    # Retrieve args
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--dataset', dest='dataset', type=int, nargs='+', default=[1, 2, 3], help='an integer associated with a data set (i.e. 4)')
    parser.add_argument('--source', dest='source', type=str, choices=['remote','local'], default='remote', help='where to gather the data for the data set(s) (local files must be named raw{ds}.json where ds is the number associated with the data set, i.e. raw2.json)')
    parser.add_argument('--season', dest='season', type=int, nargs='+', default=[], help='an integer season (only applicable with data sources 3 and 4) (i.e. 11)')
    parser.add_argument('--contestant', dest='contestant', type=str, nargs='+', default=[], help='a string contestant first and last name separated by "_" (only applicable with data source 5) (i.e. joelle_fletcher)')
    args = parser.parse_args()

    # Initialize multiprocessing pool with 5 threads
    pool = Pool(processes=5)

    # Initialize data model handler object
    bachdata = data.bachdata()

    # If source is set to local, read data in from files located in ./local/
    if args.source == 'local':
        pool_resp = pool.map_async(getlocal, args.dataset)
        df1, df2, df3 = pool_resp.get()
        # Set all ds3 record ids to match ds2
        df3 = set_ds3_ids(df2, df3)
        # Save all data set data frames
        bachdata.save_df(df1, 1)
        bachdata.save_df(df2, 2)
        bachdata.save_df(df3, 3)
    # Else, scrape the data from remote sources
    else:
        # Initialize dataframe variables
        df1 = None
        df2 = None
        df3 = None
        for ds in args.dataset:
            # Data sets 1.1 and 1.2
            if ds == 1:
                # Scrape data set 1
                ds1_data = scrape1()
                df1 = pd.DataFrame(list(ds1_data))
                # Save data set 1
                bachdata.save_df(df1, 1)
            # Data sets 2.1 and 2.2
            elif ds == 2:
                # If data set 1 hasn't been read-in to a data frame, attempt to read data set 1 from pickled file
                if not isinstance(df1, pd.DataFrame):
                    df1 = bachdata.retrieve_df(1)
                if not df1.empty:
                    seasons = []
                    for show in [0,1]:
                        try:
                            max_season = int(df1[df1['show']==show].max()['season'])
                        except TypeError:
                            print('Mayday! Unable to convert max season value to int')
                            max_season = 0
                        if max_season > 0:
                            seasons += [(show, season) for season in range(1, max_season+1)]
                        else:
                            print('Mayday! Unable to collect data set 2. Has data set 1 been collected and stored?')
                    # Multiprocess
                    ds2_resp = pool.starmap_async(scrape2, seasons)
                    ds2_data = []
                    for recs in ds2_resp.get():
                        if recs:
                            ds2_data += recs
                    df2 = pd.DataFrame(ds2_data)
                    print(len(df2))
                    # Save data set 2
                    bachdata.save_df(df2, 2)
            # Data set 3
            elif ds == 3:
                # If data set 2 hasn't been read-in to a data frame, attempt to read data set 2 from pickled file
                if not isinstance(df2, pd.DataFrame):
                    df2 = bachdata.retrieve_df(2)
                if not df2.empty:
                    contestants = df2[['id','profile_url']].values.tolist()
                    if len(contestants) > 0:
                        ds3_resp = pool.starmap_async(scrape3, contestants)
                    else:
                        print(f'Mayday! Unable to collect data set 3. Has data set 2 been collected and stored?')
                    # Multiprocess
                    df3 = pd.DataFrame([rec for rec in list(ds3_resp.get()) if rec != None])
                    # Save data set 3
                    bachdata.save_df(df3, 3)

if __name__ == '__main__':
    main()

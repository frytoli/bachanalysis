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
import datetime
import random
import model
import json
import pytz
import time
import os
import re

# Global var for path to volume within container
PATH_TO_VOLUME = os.path.join(os.getcwd(), 'data')

'''
Scrape data Sets 1.1 and 1.2
Collect general information from all seasons of The Bachelor or The Bachelorette
https://en.wikipedia.org/wiki/The_Bachelor_(American_TV_series)
https://en.wikipedia.org/wiki/The_Bachelorette
'''
def scrape1():
    # Initialize data model handler object
    bachmodel = model.bachmodel(PATH_TO_VOLUME)
    # Scrape
    scraped = wikipedia.scrape('bachelor')
    time.sleep(random.uniform(3,8))
    scraped += wikipedia.scrape('bachelorette')
    # Model the raw data
    modeled_data = bachmodel.model_many(1, scraped)
    # Return modeled json data
    return modeled_data

'''
Scrape data Sets 2.1 and 2.2
Collect general information about all contestants from one given show's (The Bachelor or The Bachelorette) given season
https://bachelor-nation.fandom.com/wiki/The_Bachelor_(Season_1)
https://bachelor-nation.fandom.com/wiki/The_Bachelorette_(Season_1)
'''
def scrape2(show, season):
    # Initialize data model handler object
    bachmodel = model.bachmodel(PATH_TO_VOLUME)
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
        modeled_data = bachmodel.model_many(2, scraped)
        # Return modeled json data
        return modeled_data

'''
Scrape data Set 3
Collect photos and additional physical information of one Bachelor/Bachelorette cast member
https://bachelor-nation.fandom.com/wiki/Alex_Michel
'''
def scrape3(id, contestant):
    # Initialize data model handler object
    bachmodel = model.bachmodel(PATH_TO_VOLUME)
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
        modeled_data = bachmodel.model_one(3, scraped)
        # Return modeled json data
        return modeled_data

'''
Compile data Set 4
Collect social media data and photos of one Bachelor/Bachelorette cast member
https://www.instagram.com
'''
def compile4(ig_api, id, contestant_ig_url):
    # Initialize data model handler object
    bachmodel = model.bachmodel(PATH_TO_VOLUME)
    # Assume asyncronous scraping
    time.sleep(random.uniform(3,8))
    # Extract instagram username from url
    username_match = re.search(r'(?<=instagram\.com/)[a-zA-Z0-9._]{1,30}', contestant_ig_url)
    if username_match:
        contestant_ig_username = username_match.group(0)
        # GET
        returned = ig_api.get_profile(contestant_ig_username)
        # Continue if response is not empty
        if len(returned) > 0:
            # Add id to raw record
            returned['id'] = id
            # Add url to record
            returned['url'] = contestant_ig_url
            # Model the raw data
            modeled_data = bachmodel.model_one(4, returned)
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
        row = df2.loc[df2['profile_url']==url]['id'].values
        if len(row) > 0:
            # Update the associated record in data set 3
            df3.loc[df3['profile_url'] == url, 'id'] = row[0]
    return df3

def set_ds4_ids(df3, df4):
    # Get instagram usernames of all documents for which to set ids
    usernames = list(df4['username'])
    for username in usernames:
        # Find record in data set 3 that has the username in an item in its social media value
        df3_res = df3.loc[df3['social_media'].apply(lambda x: any([username in y for y in x]))]
        if len(df3_res) > 0:
            # Update the associated record in data set 4
            df4.loc[df4['username']==username, ['id']] = df3_res['id'].iloc[0]
        else:
            print(f'Mayday! A record with social media {username} not found')
    return df4

def getlocal(ds):
    # Initialize data model handler object
    bachmodel = model.bachmodel(PATH_TO_VOLUME)
    # Validate existence of file
    if os.path.exists(os.path.join(PATH_TO_VOLUME, f'raw{ds}.json')):
        # Read local file in from ./data/
        with open(os.path.join(PATH_TO_VOLUME, f'raw{ds}.json'), 'r') as injson:
            raw_data = json.load(injson)
        # Model the raw data
        modeled_data = bachmodel.model_many(ds, raw_data)
        # Convert the modeled data to pandas df and returm
        return pd.DataFrame(modeled_data)
    else:
        print(f'Mayday! No input file ./data/raw{ds}.json found')

'''
Main
'''
def main():
    # Retrieve args
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--dataset', dest='dataset', type=int, nargs='+', default=[1, 2, 3, 4], help='an integer associated with a data set (i.e. 4)')
    parser.add_argument('--source', dest='source', type=str, choices=['remote','local'], default='remote', help='where to gather the data for the data set(s) (local files must be named raw{ds}.json where ds is the number associated with the data set, i.e. raw2.json)')
    parser.add_argument('--season', dest='season', type=int, nargs='+', default=[], help='an integer season (only applicable with data sources 3 and 4) (i.e. 11)')
    parser.add_argument('--contestant', dest='contestant', type=str, nargs='+', default=[], help='a string contestant first and last name separated by "_" (only applicable with data source 5) (i.e. joelle_fletcher)')
    args = parser.parse_args()

    # Initialize multiprocessing pool with 5 threads
    pool = Pool(processes=5)

    # Initialize data model handler object
    bachmodel = model.bachmodel(PATH_TO_VOLUME)

    # If source is set to local, read data in from files located in ./data/
    if args.source == 'local':
        pool_resp = pool.map_async(getlocal, args.dataset)
        df1, df2, df3, df4 = pool_resp.get()
        # Set all ds3 record ids to match ds2
        df3 = set_ds3_ids(df2, df3)
        # Set all ds4 record ids to match ds3
        df4 = set_ds4_ids(df3, df4)
        # Save all data set dataframes
        bachmodel.save_df(df1, 1)
        bachmodel.save_df(df2, 2)
        bachmodel.save_df(df3, 3)
        bachmodel.save_df(df3, 4)
    # Else, scrape the data from remote sources
    else:
        # Initialize dataframe variables
        df1 = None
        df2 = None
        df3 = None
        # Data set 1
        if 1 in args.dataset:
            # Scrape data set 1
            ds1_data = scrape1()
            df1 = pd.DataFrame(list(ds1_data))
            # Save data set 1
            bachmodel.save_df(df1, 1)
        # Data set 2
        if 2 in args.dataset:
            # If data set 1 hasn't been read-in to a dataframe, attempt to read data set 1 from pickled file
            if not isinstance(df1, pd.DataFrame):
                df1 = bachmodel.retrieve_df(1)
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
                # Save data set 2
                bachmodel.save_df(df2, 2)
        # Data set 3
        if 3 in args.dataset:
            # If data set 2 hasn't been read-in to a dataframe, attempt to read data set 2 from pickled file
            if not isinstance(df2, pd.DataFrame):
                df2 = bachmodel.retrieve_df(2)
            if not df2.empty:
                contestants = df2[['id','profile_url']].values.tolist()
                if len(contestants) > 0:
                    ds3_resp = pool.starmap_async(scrape3, contestants)
                else:
                    print(f'Mayday! Unable to collect data set 3. Has data set 2 been collected and stored?')
                # Multiprocess
                df3 = pd.DataFrame([rec for rec in list(ds3_resp.get()) if rec != None])
                # Save data set 3
                bachmodel.save_df(df3, 3)
        # Data set 4
        if 4 in args.dataset:
            # If data set 3 hasn't been read-in to a dataframe, attempt to read data set 3 from pickled file
            if not isinstance(df3, pd.DataFrame):
                df3 = bachmodel.retrieve_df(3)
            if not df3.empty:
                # Initialize instagram api object
                ig = instagram.api(os.path.join(PATH_TO_VOLUME, 'ig.cfg'))
                # Retrieve contestants' social media information from data set 3
                contestants = df3[df3['social_media'].str.len() > 0][['id','social_media']].values.tolist()
                contestants_igs = []
                for contestant in contestants:
                    for url in contestant[1]:
                        if 'instagram' in url.lower():
                            contestants_igs.append((ig, contestant[0], url))
                if len(contestants_igs) > 0:
                    ds4_resp = pool.starmap_async(compile4, contestants_igs)
                else:
                    print(f'Mayday! Unable to collect data set 4. Has data set 3 been collected and stored?')
                # Multiprocess
                df4 = pd.DataFrame([rec for rec in list(ds4_resp.get()) if rec != None])
                # Save data set 4
                bachmodel.save_df(df4, 4)


if __name__ == '__main__':
    main()

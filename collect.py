#!/usr/bin/env python

'''
* Data collection
* Facilitate the conversion of raw data into the data model format (json)
* Facilitate the storage of modeled data (pickled (serialized) pandas dataframes)
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
if not os.path.exists(PATH_TO_VOLUME):
    os.mkdir(PATH_TO_VOLUME)

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
https://www.instagram.com (Undocumented Instagram API)
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
Main
'''
def main():
    # Retrieve args
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--dataset', dest='dataset', type=int, nargs='+', default=[1, 2, 3, 4], help='an integer associated with a data set (i.e. 4)')
    parser.add_argument('--season', dest='season', type=int, nargs='+', default=[], help='an integer season (only applicable with data source 2) (i.e. 11)')
    parser.add_argument('--contestant', dest='contestant', type=str, nargs='+', default=[], help='a string contestant first and last name separated by "_" (only applicable with data sources 3 and 4) (i.e. joelle_fletcher)')
    args = parser.parse_args()

    # Initialize multiprocessing pool with 5 threads
    pool = Pool(processes=5)

    # Initialize data model handler object
    bachmodel = model.bachmodel(PATH_TO_VOLUME)

    # Initialize dataframe variables
    df1 = None
    df2 = None
    df3 = None
    # Data set 1
    if 1 in args.dataset:
        print('🌹 Collecting data set 1')
        # Scrape data set 1
        ds1_data = scrape1()
        df1 = pd.DataFrame(list(ds1_data))
        # Save data set 1
        bachmodel.save_df(df1, 1)
    # Data set 2
    if 2 in args.dataset:
        print('🌹 Collecting data set 2')
        seasons = []
        # If season argument is specified, collect only the given seasons
        if len(args.season) > 0:
            for show in [0,1]:
                seasons += [(show, season) for season in args.season]
        # Otherwise, collect all seasons available from data set 1
        else:
            # If data set 1 hasn't been read-in to a dataframe, attempt to read data set 1 from pickled file
            if not isinstance(df1, pd.DataFrame):
                df1 = bachmodel.retrieve_df(1)
            if not df1.empty:
                for show in [0,1]:
                    try:
                        max_season = int(df1[df1['show']==show].max()['season'])
                    except TypeError:
                        print('  💔 Unable to convert max season value to int')
                        max_season = 0
                    if max_season > 0:
                        seasons += [(show, season) for season in range(1, max_season+1)]
                    else:
                        print('  💔 Unable to collect data set 2. Has data set 1 been collected and stored?')
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
        print('🌹 Collecting data set 3')
        contestants = []
        # If data set 2 hasn't been read-in to a dataframe, attempt to read data set 2 from pickled file
        if not isinstance(df2, pd.DataFrame):
            df2 = bachmodel.retrieve_df(2)
        if not df2.empty:
            # If contestant argument is specified, collect only the given contestants
            if len(args.contestant) > 0:
                for contestant in args.contestant:
                    # Find contestant information and save
                    name = f'''{contestant.split('_')[0][0].upper()}{contestant.split('_')[0][1:].lower()} {contestant.split('_')[1][0].upper()}{contestant.split('_')[1][1:].lower()}'''
                    contestant = df2[df2['name'] == name][['id', 'profile_url']].values.tolist()
                    contestants += contestant
            # Else, collect all contestants available from data set 2
            else:
                contestants = df2[['id','profile_url']].values.tolist()
                if len(contestants) == 0:
                    print(f'  💔 Unable to collect data set 3. Has data set 2 been collected and stored?')
        # Multiprocess
        ds3_resp = pool.starmap_async(scrape3, contestants)
        df3 = pd.DataFrame([rec for rec in list(ds3_resp.get()) if rec != None])
        # Save data set 3
        bachmodel.save_df(df3, 3)
    # Data set 4
    if 4 in args.dataset:
        print('🌹 Collecting data set 4')
        contestants_igs = []
        # Initialize instagram api object
        ig = instagram.api(os.path.join(PATH_TO_VOLUME, 'ig.cfg'))
        # If data set 3 hasn't been read-in to a dataframe, attempt to read data set 3 from pickled file
        if not isinstance(df3, pd.DataFrame):
            df3 = bachmodel.retrieve_df(3)
        if not df3.empty:
            # If contestant argument is specified, collect only the given contestants
            if len(args.contestant) > 0:
                for contestant in args.contestant:
                    # Find contestant information and save
                    name = f'''{contestant.split('_')[0][0].upper()}{contestant.split('_')[0][1:].lower()} {contestant.split('_')[1][0].upper()}{contestant.split('_')[1][1:].lower()}'''
                    contestant = df3[df3['name'] == name][['id','social_media']].values.tolist()[0]
                    for url in contestant[1]:
                        if 'instagram' in url.lower():
                            contestants_igs.append((ig, contestant[0], url))
            # Else, collect all contestants available from data set 3
            else:
                # Retrieve contestants' social media information from data set 3
                contestants = df3[df3['social_media'].str.len() > 0][['id','social_media']].values.tolist()
                contestants_igs = []
                for contestant in contestants:
                    for url in contestant[1]:
                        if 'instagram' in url.lower():
                            contestants_igs.append((ig, contestant[0], url))
                if len(contestants_igs) == 0:
                    print(f'  💔 Unable to collect data set 4. Has data set 3 been collected and stored?')
        # Multiprocess
        ds4_resp = pool.starmap_async(compile4, contestants_igs)
        df4 = pd.DataFrame([rec for rec in list(ds4_resp.get()) if rec != None])
        # Save data set 4
        bachmodel.save_df(df4, 4)


if __name__ == '__main__':
    main()

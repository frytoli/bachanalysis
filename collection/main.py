#!/usr/local/bin/python3

from multiprocessing import Pool
from scrapers import *
import argparse

'''
Collect general information from all seasons of The Bachelor
https://en.wikipedia.org/wiki/The_Bachelor_(American_TV_series)
'''
def scrape1():
    resp = ds1.scrape()
    return resp

'''
Collect general information from all seasons of The Bachelorette
https://en.wikipedia.org/wiki/The_Bachelorette
'''
def scrape2():
    resp = ds2.scrape()
    return resp

'''
Collect general information about all contestants from a given season or all seasons of The Bachelor
https://en.wikipedia.org/wiki/The_Bachelor_(season_1)
'''
def scrape3(season):
    resp = scrapers.ds3()
    return resp

'''
Collect general information about all contestants from a given season or all seasons of The Bachelorette
https://en.wikipedia.org/wiki/The_Bachelorette_(season_1)
'''
def srcape4(season):
    resp = scrapers.ds4()
    return resp

'''
Collect photos and additional physical information of one Bachelor/Bachelorette cast member or all Bachelor/Bachelorette cast members
https://bachelor-nation.fandom.com/wiki/Alex_Michel
'''
def scrape5(contestant):
    resp = scrapers.ds5()
    return resp

def main():
    # Retrieve args
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('scraper', metavar='N', type=int, nargs='+', help='an integer associated with a data source (i.e. 4)')
    parser.add_argument('--season', dest='seasons', type=int, action='store', default=[None], help='an integer season (only applicable with data sources 3 and 4) (i.e. 11)')
    parser.add_argument('--contestant', dest='contestants', type=str, action='store', default=[None], help='a string contestant first and last name separated by "_" or "-" (only applicable with data source 5) (i.e. joelle_fletcher)')
    args = parser.parse_args()

    scrape1()

    '''
    # Initialize multiprocessing pool with 5 threads
    pool = Pool(processes=5)
    # Run asyncronous processes
    if 1 in args['scraper']:
        ds1_resp = pool.map_async(scrape1)
    if 2 in args['scraper']:
        ds2_resp = pool.map_async(scrape2)
    if 3 in args['scraper']:
        if type(args['season']) != list:
            args['season'] = [args['season']]
        ds3_resp = pool.map_async(scrape3, args['season'])
    if 4 in args['scraper']:
        if type(args['season']) != list:
            args['season'] = [args['season']]
        ds4_resp = pool.map_async(scrape4, args['season'])
    if 5 in args['scraper']:
        if type(args['contestant']) != list:
            args['contestant'] = [args['contestant']]
        ds5_resp = pool.map_async(scrape5, args['contestant'])
    '''


if __name__ == '__main__':
    main()

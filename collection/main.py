#!/usr/local/bin/python3

import argparse

def main():
    # Retrieve args
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('scraper', metavar='N', type=int, nargs='+', help='an integer associated with a data source (i.e. 4)')
    parser.add_argument('--season', dest='seasons', action='store', default=[], help='an integer season (only applicable with data sources 3 and 4) (i.e. 11)')
    parser.add_argument('--contestant', dest='contestants', action='store', default=[], help='a string contestant first and last name separated by "_" or "-" (only applicable with data source 5) (i.e. joelle_fletcher)')
    args = parser.parse_args()



if __name__ == '__main__':
    main()

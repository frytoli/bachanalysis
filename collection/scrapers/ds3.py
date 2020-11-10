#!/usr/bin/env python

from bs4 import BeautifulSoup
import pandas as pd
import requests
import random

def select_ua():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)',
        'Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0;  Trident/5.0)',
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0; MDDCJS)',
        'Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko'
    ]
    return random.choice(user_agents)

def scrape_season(season):
    url = f'https://en.wikipedia.org/wiki/The_Bachelor_(season_{season})'
    # Get url and save DOM
    dom = requests.get(
            url,
            headers={'User-Agent':select_ua()}
        ).text

    # Account for no page for the query
    if 'Wikipedia does not have an article with this exact name' in dom:
        print(f'Wikipedia does not have an article at {url}. Skipping.')
        return None
    else:
        # Soup-ify the returned source
        soup = BeautifulSoup(dom, 'html.parser')
        # Parse out contestants table
        table = soup.find('table', class_='wikitable sortable')
        if table:
            # Convert html table to dataframe
            df = pd.read_html(str(table), header=0)[0]
            # Normalized and remove any special characters from column names
            df = df.rename(columns={col: f'''{col.strip().replace('(','').replace(')','').replace(':','').replace('-','').replace(' ','_').lower()}''' for col in df.columns})
            # Rename job column to occupation if applicable
            if 'occupation' in df.columns:
                df = df.rename(columns={'job':'occupation'})
            # Convert dataframe to dict
            data = [record for record in df.to_dict(orient='records')]
            return data
        else:
            print(f'Table does not exist at {url}. Skipping.')
            return None

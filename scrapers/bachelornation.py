#!/usr/bin/env python

from bs4 import BeautifulSoup
import pandas as pd
import requests
import random
import base64
import re

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

def scrape_season(show, season):
    # Initialize list of contestants
    contestants = []
    # Select URL
    if show == 'bachelor':
        url = f'https://bachelor-nation.fandom.com/wiki/The_Bachelor_(Season_{season})'
    elif show == 'bachelorette':
        url = f'https://bachelor-nation.fandom.com/wiki/The_Bachelorette_(Season_{season})'
    # Get url and save DOM
    dom = requests.get(
            url,
            headers={'User-Agent':select_ua()}
        ).text
    # Soup-ify the returned source
    soup = BeautifulSoup(dom, 'html.parser')

    # Check that there is contents on the page
    alert_div = soup.find('div', class_='noarticletext mw-content-ltr')
    if alert_div:
        print(f'No contents on page for {season}. Skipping.')
    else:
        # Define list of known keys
        keys = ['name', 'age', 'hometown', 'occupation', 'eliminated']
        # Check for gallery style (common with newer season pages)
        gallery_items = soup.findAll('div', class_='wikia-gallery-item')
        if len(gallery_items) > 20:
            # Iterate over gallery items and save info
            for item in gallery_items:
                caption = item.find('div', class_='lightbox-caption')
                if caption:
                    name = caption.find('a')
                    if name:
                        profile_url = f'''https://bachelor-nation.fandom.com{name['href']}'''
                        values = re.split(r'<br\/{0,1}>', str(caption))
                        if len(values) == 5:
                            # Compile html tag removal regex pattern
                            tag_pattern = re.compile(r'</{0,1}[a-z]{1,5}>')
                            contestants.append({
                                keys[0]: tag_pattern.sub('', name.text),
                                keys[1]: int(tag_pattern.sub('', values[1].strip())),
                                keys[2]: tag_pattern.sub('', values[2].strip()),
                                keys[3]: tag_pattern.sub('', values[3].strip()),
                                keys[4]: tag_pattern.sub('', values[4].strip()),
                                'profile_url': tag_pattern.sub('', profile_url),
                                'season': season,
                                'show': show
                            })
            return contestants
        # Else, check for table style (commone with older season pages)
        else:
            article_tables = soup.findAll('table', class_='article-table')
            if len(article_tables) > 0:
                # Iterate over tables and check headers
                for table in article_tables:
                    # Convert html table to dataframe
                    df = pd.read_html(str(table), header=0)[0]
                    # Check if column headers are expected
                    if [col.strip().lower() for col in list(df.columns)] == keys:
                        # We have confirmed we have the correct table of contestants
                        # Normalized column names
                        df = df.rename(columns={col: col.strip().lower() for col in df.columns})
                        # Add profile_url column
                        df['profile_url'] = [f'''https://bachelor-nation.fandom.com{a['href']}''' for a in table.findAll('a')]
                        # Add season column
                        df['season'] = [season for i in range(len(df.index))]
                        # Add show column
                        df['show'] = [show for i in range(len(df.index))]
                        # Convert dataframe to dict
                        contestants = [record for record in df.to_dict(orient='records')]
                        return contestants
    return contestants

def scrape_contestant(contestant):
    # Initialize data dictionary
    data = {}
    # Check if url or name was given
    if not contestant.startswith('http'):
        # Normalize contestant name
        contestant = f'''{contestant[0].upper()}{contestant.split('_')[0][1:]}_{contestant.split('_')[1][0].upper()}{contestant.split('_')[1][1:]}'''
        contestant = f'https://bachelor-nation.fandom.com/wiki/{contestant}'
    # Get url and save DOM
    dom = requests.get(
            contestant,
            headers={'User-Agent':select_ua()}
        ).text
    # Soup-ify the returned source
    soup = BeautifulSoup(dom, 'html.parser')

    # Check that there is contents on the page
    alert_div = soup.find('div', class_='noarticletext mw-content-ltr')
    if alert_div:
        print(f'No contents on page for {contestant}. Skipping.')
    else:
        # Parse out headshot
        headshot = soup.find('img', class_='pi-image-thumbnail')
        headshot_b64 = None
        if headshot:
            headshot_src = headshot['src']
            # Download image in temp file
            r = requests.get(
                headshot_src,
                headers={'User-Agent':select_ua()}
            )
            img = f"data:{r.headers['Content-Type']};base64,{base64.b64encode(r.content).decode('utf-8')}"
            # Clean memory
            del r
            # Save base64 encoded image in json record
            data['photo'] = img
        # Parse out additional categorized info
        infos = soup.findAll('div', class_='pi-item pi-data pi-item-spacing pi-border-color')
        for pair in infos:
            key = pair.find('h3').text.strip()
            value = pair.find('div')
            # If key is social_media, retrieve and save all social media links
            if key.lower() == 'social media':
                value = f'''{', '.join([a['href'] for a in value.findAll('a')])}'''
            # Otherwise, save the text
            else:
                value = value.text
            data[key] = value
        # Attempt to find height information included in wiki content
        content = soup.find('div', id='content')
        ps = content.findAll('p')
        for p in ps:
            b = p.find('b')
            i = p.find('i')
            if b and b.text.strip().lower() == 'height':
                data['height'] = p.text.lower().replace(b.text.strip().lower(),'').strip()
                if i:
                    data['height'] = data['height'].replace(i.text.strip().lower(),'')
    return data

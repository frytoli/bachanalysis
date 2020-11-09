#!/usr/local/bin/python3

from bs4 import BeautifulSoup
import requests
import random
import base64

def normalize_name(contestant):
    name = contestant.split('_')
    return f'{name[0][0].upper()}{name[0][1:].lower()}_{name[1][0].upper()}{name[1][1:].lower()}'

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

def scrape_contestant(contestant):
    # Normalize contestant name for url
    contestant = normalize_name(contestant)
    url = f'https://bachelor-nation.fandom.com/wiki/{contestant}'
    # Get url and save DOM
    dom = requests.get(
            url,
            headers={'User-Agent':select_ua()}
        ).text
    # Soup-ify the returned source
    soup = BeautifulSoup(dom, 'html.parser')
    # Initialize data dictionary
    data = {}
    # Parse out headshot
    headshot = soup.find('img', class_='pi-image-thumbnail')
    headshot_b64 = None
    if headshot:
        headshot_src = headshot['src']
        # Download image in temp file
        ext = headshot_src.split('.')[-1].split('/')[0]
        r = requests.get(
            headshot_src,
            headers={'User-Agent':select_ua()}
        )
        img = f"data{r.headers['Content-Type']};base64,{base64.b64encode(r.content).decode('utf-8')}"
        # Clean memory
        del r
        # Save base64 encoded image in json record
        data['photo'] = img
    # Parse out additional categorized info
    infos = soup.findAll('div', class_='pi-item pi-data pi-item-spacing pi-border-color')
    for pair in infos:
        key = pair.find('h3').text
        value = pair.find('div').text
        data[key] = value
    # Return
    return data

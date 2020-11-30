#!/usr/bin/env python

import configparser
import datetime
import requests
import base64
import ssl

class api():
    def __init__(self, configfile):
        # Retrieve Instagram username/password from file
        config = configparser.ConfigParser()
        config.read(configfile)
        username = config.get('Instagram', 'username')
        password = config.get('Instagram', 'password')
        # Authenticate with Instagram
        time = int(datetime.datetime.now().timestamp())
        r = requests.get('https://www.instagram.com')
        xcsrftoken = r.cookies['csrftoken']
        # Keep headers consistent
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:82.0) Gecko/20100101 Firefox/82.0',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://www.instagram.com/accounts/login/',
            'x-csrftoken': xcsrftoken
        }
        login_r = requests.post(
            'https://www.instagram.com/accounts/login/ajax/',
            data={
                'username': username,
                'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{time}:{password}',
                'queryParams': {},
                'optIntoOneTap': 'false'
            },
            headers=self.headers
        )
        # If http status code is good, continue
        if login_r:
            try:
                rjson = login_r.json()
            except:
                rjson = None
            if rjson['authenticated']:
                self.is_authed = True
                cookies = login_r.cookies
                cookiejar = cookies.get_dict()
                self.csrftoken = cookiejar['csrftoken']
                self.sessionid = cookiejar['sessionid']
            else:
                print('  💔 Instagram auth not successful')
                self.is_authed = False
                self.csrftoken = None
                self.sessionid = None
        else:
            print('  💔 Instagram auth not successful due to an HTTPError')
            self.is_authed = False
            self.csrftoken = None
            self.sessionid = None

    def get_profile(self, username):
        # Prepare data var
        data = {}
        # If the object has been authenticated with Instagram, continue
        if self.is_authed:
            # Retreive data from api
            try:
                r = requests.get(
                        f'https://www.instagram.com/{username}/?__a=1',
                        headers=self.headers,
                        cookies={
                            'sessionid': self.sessionid,
                            'csrftoken': self.csrftoken
                        }
                    )
            except (ssl.SSLEOFError, requests.exceptions.HTTPError):
                # Wait and try once more
                time.sleep(3)
                try:
                    r = requests.get(
                            f'https://www.instagram.com/{username}/?__a=1',
                            headers=self.headers,
                            cookies={
                                'sessionid': self.sessionid,
                                'csrftoken': self.csrftoken
                            }
                        )
                except (ssl.SSLEOFError, requests.exceptions.HTTPError):
                    print(f'  💔 SSLEOFError or HTTPError prevented retrieving Instagram profile information for {usename}')
                    return {}
            # Ensure that json data was returned
            try:
                ig_data = r.json()
            except ValueError:
                print(f'  💔 Response from Instagram for user {usename} could not be converted to json')
                return {}
            # Continue if good http status code response
            if r:
                # Parse the returned data and add it to data
                if 'graphql' in ig_data.keys():
                    if 'user' in ig_data['graphql']:
                        data['username'] = username
                        graphql = ig_data['graphql']['user']
                        try:
                            data['followers'] = int(graphql['edge_followed_by']['count'])
                        except:
                            data['followers'] = None
                        try:
                            data['following'] = int(graphql['edge_follow']['count'])
                        except:
                            data['following'] = None
                        data['name'] = graphql['full_name']
                        data['user_id'] = graphql['id']
                        # Download and save profile photo
                        r = requests.get(
                            graphql['profile_pic_url_hd'],
                            headers=self.headers,
                            cookies={
                                'sessionid': self.sessionid,
                                'csrftoken': self.csrftoken
                            }
                        )
                        if r:
                            prof_pic = f"data:{r.headers['Content-Type']};base64,{base64.b64encode(r.content).decode('utf-8')}"
                        else:
                            prof_pic = None
                        data['prof_photo'] = prof_pic
                        del prof_pic
                        # Check if user is private/public
                        data['is_private'] = graphql['is_private']
                        if not data['is_private']:
                            timeline = graphql['edge_owner_to_timeline_media']
                            try:
                                data['post_count'] = int(timeline['count'])
                            except:
                                data['post_count'] = None
                            # Retreive and save three most recent photos
                            if 'edges' in timeline:
                                edges = timeline['edges']
                                itr = 0
                                photo_count = 0
                                while photo_count < 3 and itr<len(edges):
                                    post = edges[itr]['node']
                                    if not post['is_video']:
                                        photo_count += 1
                                        # Download and save photo
                                        try:
                                            r = requests.get(
                                                post['display_url'],
                                                headers={
                                                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:82.0) Gecko/20100101 Firefox/82.0'
                                                }
                                            )
                                        except Exception as e:
                                            print(f'  💔 {e}')
                                        if r:
                                            photo = f"data:{r.headers['Content-Type']};base64,{base64.b64encode(r.content).decode('utf-8')}"
                                        else:
                                            photo = None
                                        data[f'photo{photo_count}'] = photo
                                        del photo
                                        data[f'photo{photo_count}_comments_disabled'] = post['comments_disabled']
                                        data[f'photo{photo_count}_timestamp'] = post['taken_at_timestamp']
                                        try:
                                            data[f'photo{photo_count}_comments'] = int(post['edge_media_to_comment']['count'])
                                        except:
                                            data[f'photo{photo_count}_comments'] = None
                                        try:
                                            data[f'photo{photo_count}_likes'] = int(post['edge_liked_by']['count'])
                                        except:
                                            data[f'photo{photo_count}_likes'] = None
                                    itr += 1
            # Return
            return data
        else:
            print('Instagram user is not authenticated')
            return data

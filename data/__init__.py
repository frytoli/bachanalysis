#!/usr/bin/env python

'''
* Convert raw input json data into modeled json data
'''

import pandas as pd
import json
import math
import uuid
import re
import os

class bachdata():
    def __init__(self):
        # Data model references for all data sets
        self.models = {
            1: {
                'season': 0, # -1 for null
                'original_run': '', # '' for null
                'suitor': '', # '' for null
                'winner': '', # '' for null
                'runnersup': '', # '' for null
                'proposal': 0, # 0 for no, 1 for yes, -1 for null
                'show': 0, # 0 for Bachelor, 1 for Bachelorette, -1 for null
                'still_together': 0, # 0 for no, 1 for yes, -1 for null
                'relationship_notes':'' # '' for null
            },
            2: {
                'id': '',
                'name': '', # '' for null
                'age': 0, # -1 for null
                'hometown': '', # '' for null
                'occupation': '', # '' for null
                'eliminated': '', # '' for null
                'season': 0, # -1 for null
                'show': 0, # 0 for Bachelor, 1 for Bachelorette, -1 for null
                'profile_url': '',
                'place': 0 # -1 for null
            },
            3: {
                'id': '',
                'name': '', # '' for null
                'photo': '', # '' for null
                'profile_url': '', # '' for null
                'born': '', # '' for null
                'hometown': '', # '' for null
                'occupation': '', # '' for null
                'seasons': '', # '' for null
                'social_media': '', # '' for null
                'height': '' # '' for null
            },
            4: {
                'id': '',
                'name': '', # '' for null
                'handle': '',  # '' for null
                'followers': 0, # -1 for null
                'following': 0 # -1 for null
            },
            5: {
                'id': '',
                'name': '', # '' for null
                'dlib_landmarks': '', # '' for null
                'face_photo': '', # '' for null
                'face_height': 0, # 0 for null
                'face_width': 0, # 0 for null
                'theoretical_thirds': 0.0, # 0.0 for null
                'experimental_thirds1': 0.0, # 0.0 for null
                'experimental_thirds2': 0.0, # 0.0 for null
                'experimental_thirds3': 0.0, # 0.0 for null
                'theoretical_fifths': 0.0, # 0.0 for null
                'experimental_fifths1': 0.0, # 0.0 for null
                'experimental_fifths2': 0.0, # 0.0 for null
                'experimental_fifths3': 0.0, # 0.0 for null
                'experimental_fifths4': 0.0, # 0.0 for null
                'experimental_fifths5': 0.0, # 0.0 for null
                'hw_ratio': 0.0, # 0.0 for null
                'v1_ratio': 0.0, # 0.0 for null
                'v2_ratio': 0.0, # 0.0 for null
                'v3_ratio': 0.0, # 0.0 for null
                'v4_ratio': 0.0, # 0.0 for null
                'v5_ratio': 0.0, # 0.0 for null
                'v6_ratio': 0.0, # 0.0 for null
                'v7_ratio': 0.0, # 0.0 for null
                'h1_ratio': 0.0, # 0.0 for null
                'h2_ratio': 0.0, # 0.0 for null
                'h3_ratio': 0.0, # 0.0 for null
                'h4_ratio': 0.0, # 0.0 for null
                'h5_ratio': 0.0, # 0.0 for null
                'h6_ratio': 0.0, # 0.0 for null
                'h7_ratio': 0.0 # 0.0 for null
            }
        }
        # Global var for path to volume within container
        self.PATH_TO_VOLUME = os.path.join(os.getcwd(), 'local')

    def save_df(self, df, ds):
        try:
            df.to_pickle(os.path.join(self.PATH_TO_VOLUME, f'ds{ds}.pkl'))
            return True
        except Exception as e:
            print(f'Mayday! {e}')
            return False

    def retrieve_df(self, ds):
        try:
            df = pd.read_pickle(os.path.join(self.PATH_TO_VOLUME, f'ds{ds}.pkl'))
            return df
        except Exception as e:
            print(f'Mayday! {e}')
            # Return an empty dataframe
            return pd.DataFrame({'A' : []})

    # Evaluate and set the place of each contestant in a season
    def set_place(self, data):
        # Split data into shows/seasons
        seasons_data = {}
        for item in data:
            key = f'''{item['show']}{item['season']}'''
            if key not in seasons_data:
                seasons_data[key] = [item]
            else:
                seasons_data[key].append(item)
        # Iterate over seasons, evaluate places, and compile a list
        places = []
        for show_season, season_data in seasons_data.items():
            # Get the elimination weeks
            eliminated = [row['eliminated'] for row in season_data if row['eliminated'] not in ['winner', 'runnerup']]
            # Order the list in reverse order
            eliminated = sorted(eliminated, reverse=True)
            # Insert winner and runner-up at indices 0 and 1 respectively
            eliminated.insert(0, 'winner')
            eliminated.insert(1, 'runnerup')
            # Update season_data
            for contestant in season_data:
                try:
                    # Place of contestant is the index of the contestant's elimination week in "eliminated" + 1
                    place = eliminated.index(contestant['eliminated'])+1
                    contestant['place'] = int(place)
                except ValueError:
                    contestant['place'] = -1
                places.append(contestant)
        return places

    # Model provided json (dict) data
    def model_one(self, ds, data):
        elimination_week_pattern = re.compile(r'winner|runner-{0,1}up|week [1-9][0-9]{0,1}|episode [1-9][0-9]{0,1}')
        modeled_data = {}
        # Ensure the data is json
        if type(data) == dict:
            # Normalize keys in data
            data = {key.replace('(','').replace(')','').replace(':','').replace('-','').replace(' ','_').lower():value for key, value in data.items()}
            for key, value in self.models[ds].items():
                if key in data:
                    # Handle data specific data manipulations
                    if key == 'show':
                        if type(data[key]) == str:
                            if 'bachelorette' in data[key].lower():
                                modeled_data[key] = 1
                            elif 'bachelor' in data[key].lower():
                                modeled_data[key] = 0
                            else:
                                print(f'Value {data[key]} was not able to be evaluated as The Bachelor or The Bachelorette')
                                modeled_data[key] = -1
                        else:
                            if math.isnan(data[key]):
                                modeled_data[key] = -1
                            else:
                                print(f'Value {data[key]} was not able to be evaluated as The Bachelor or The Bachelorette')
                                modeled_data[key] = -1
                    elif key == 'proposal' or key == 'still_together':
                        if type(data[key]) == str:
                            if 'yes' in data[key].lower():
                                modeled_data[key] = 1
                            elif 'no' in data[key].lower():
                                modeled_data[key] = 0
                            else:
                                print(f'Value {data[key]} was not able to be evaluated as yes or no')
                                modeled_data[key] = -1
                        else:
                            if math.isnan(data[key]):
                                modeled_data[key] = -1
                            else:
                                print(f'Value {data[key]} was not able to be evaluated as yes or no')
                                modeled_data[key] = -1
                    elif key == 'eliminated':
                         if type(data[key]) == float and math.isnan(data[key]):
                             modeled_data[key] = ''
                         else:
                            try:
                                elimination_str = elimination_week_pattern.findall(data[key].lower())
                                if len(elimination_str) > 0:
                                    # Save last instance of regex pattern match
                                    modeled_data[key] = elimination_str[-1].replace('episode','week').replace('-','')
                                else:
                                    modeled_data[key] = ''
                            except ValueError:
                                modeled_data[key] = ''
                                print(f'Value {data[key]} was not able to be cast to string')
                    else:
                        if type(data[key]) == float and math.isnan(data[key]):
                            if type(value) == int:
                                modeled_data[key] = -1
                            elif type(value) == str:
                                modeled_data[key] = ''
                        else:
                            try:
                                modeled_data[key] = type(value)(data[key])
                            except ValueError:
                                if type(value) == int:
                                    modeled_data[key] = -1
                                    print(f'Value {data[key]} was not able to be cast to integer')
                                elif type(value) == str:
                                    modeled_data[key] = ''
                                    print(f'Value {data[key]} was not able to be cast to string')
                else:
                    # If id has not yet been set, set it now (this should only be applicable when modeling data set 2)
                    if key == 'id':
                        modeled_data[key] = str(uuid.uuid4())
                    else:
                        modeled_data[key] = value
        else:
            print('Mayday! Only a json object is permitted')
            return {}
        # If the resulting json object (dict) only contains null values, return an empty dict
        if modeled_data == self.models[ds]:
            modeled_data = {}
        return modeled_data

    # Model provided list of json (dict) objects data
    def model_many(self, ds, datas):
        # Ensure the data is json
        if type(datas) == list and len(datas) > 0 and type(datas[0]) == dict:
            # Model the data
            modeled_datas = []
            for data in datas:
                modeled_data = self.model_one(ds, data)
                # Only save objects that are not empty
                if modeled_data != {}:
                    modeled_datas.append(modeled_data)
            # Set places of contestants in data set 2
            if ds == 2:
                modeled_datas = self.set_place(modeled_datas)
            return modeled_datas
        else:
            print('Mayday! Only a list of json objects are permitted')
            return []
        return modeled_datas

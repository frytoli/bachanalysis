#!/usr/bin/env python

'''
* Convert raw input json data into modeled json data
'''

import json
import math

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
                'name': '', # '' for null
                'photo': '', # '' for null
                'born': '', # '' for null
                'hometown': '', # '' for null
                'occupation': '', # '' for null
                'seasons': '', # '' for null
                'social_media': '', # '' for null
                'height': '' # '' for null
            },
            4: {
                'temp': ''
            },
            5: {
                'name': '',
                'dlib_landmarks': '',
                'face_photo': ''
            }
        }

    # Return a list of lists containing a data set's key names and associated python value types
    def get_sql_table_values(self, ds):
        sql_values = []
        for key, value in self.models[ds].items():
            if type(value) == str:
                sql_values.append([key, 'text'])
            elif type(value) == int:
                sql_values.append([key, 'integer'])
        return sql_values

    # Model provided json (dict) data
    def model_one(self, ds, data):
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
                                modeled_data[key] = type(value)(data[key].lower().replace('eliminated in ',''))
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
            return modeled_datas
        else:
            print('Mayday! Only a list of json objects are permitted')
            return []
        return modeled_datas

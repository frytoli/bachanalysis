#!/usr/bin/env python

'''
* Convert input data into json data model
'''

import pandas as pd
import json

class bachdata():
    def __init__(self):
        # Data model references for all data sets
        self.models = {
            1: {
                'season': 0,
                'original_run': '',
                'suitor': '',
                'winner': '',
                'runnersup': '',
                'proposal': 0, # 0 for no, 1 for yes
                'show': 0, # 0 for Bachelor, 1 for Bachelorette
                'still_together': 0, # 0 for no, 1 for yes
                'relationship_notes':''
            },
            2: {
                'name': '',
                'age': 0,
                'hometown': '',
                'occupation': '',
                'eliminated': '',
                'season': 0,
                'show': 0, # 0 for Bachelor, 1 for Bachelorette
                'profile_url': '',
                'place': 0
            },
            3: {
                'name': '',
                'photo': '',
                'born': '',
                'hometown': '',
                'occupation': '',
                'seasons': '',
                'social_media': '',
                'height': ''
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

    # Convert dict (json) data into a document or list of documents ready to be inserted into the database
    def dict_to_doc(self, ds, data):
        doc = []
        # Ensure the data is json
        if type(data) == dict:
            for key, value in self.models[ds].items():
                if key in data:
                    # Handle data specific data manipulations
                    if key == 'show':
                        if 'bachelorette' in data[key].lower():
                            doc.append(1)
                        elif 'bachelor' in data[key].lower():
                            doc.append(0)
                        else:
                            print(f'Value {data[key]} was not able to be evaluated as The Bachelor or The Bachelorette')
                            doc.append(-1)
                    elif key == 'proposal' or key == 'still_together':
                        if not type(data[key]) == str:
                            print(f'Value {data[key]} was not able to be evaluated as yes or no')
                            doc.append(-1)
                        elif 'yes' in data[key].lower():
                            doc.append(1)
                        elif 'no' in data[key].lower():
                            doc.append(0)
                        else:
                            print(f'Value {data[key]} was not able to be evaluated as yes or no')
                            doc.append(-1)
                    else:
                        try:
                            doc.append(type(value)(data[key]))
                        except ValueError:
                            if type(value) == int:
                                doc.append(-1)
                                print(f'Value {data[key]} was not able to be cast to integer')
                            elif type(value) == str:
                                doc.append('')
                                print(f'Value {data[key]} was not able to be cast to string')
                else:
                    doc.append(value)
        else:
            print('Mayday! Only dict (json) data is permitted')
        return doc

    # Convert database documents (list of tuples) to dict (json)
    def doc_to_dict(self, ds, doc):
        data = {}
        i = 0
        for key, value in self.models[ds].items():
            if len(doc) > i:
                try:
                    data[key] = type(value)(doc[i])
                except ValueError:
                    if type(value) == int:
                        data[key] = -1
                        print(f'Value {doc[i]} was not able to be cast to integer')
                    elif type(value) == str:
                        data[key] = ''
                        print(f'Value {doc[i]} was not able to be cast to string')
                i += 1
            else:
                if type(value) == int:
                    data[key] = -1
                    print(f'Nov value for {key} was found in the given document')
                elif type(value) == str:
                    data[key] = ''
                    print(f'Nov value for {key} was found in the given document')
        return data

    def csv_to_db(self):
        # Prepare csv data to be inserted into bachelor database
        pass

    def db_to_csv(self): # Maybe
        # Export database data as csv
        pass

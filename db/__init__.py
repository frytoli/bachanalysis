#!/usr/bin/env python

'''
Handle data storage in SQL database
* Create tables from an input list of tuple values
* Insert given json data into a given table
* Retreive data from a given table and return as a list of tuples
* Retreive max value of a given column in a table and return as an integer
'''

import sqlite3

class bachdb():
    def __init__(self, dbname):
        # Hardcode database name
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)
        self.cur = self.conn.cursor()

    def __prepare_conditional_str(self, table, conditionals):
        # Ensure that all keys in the given conditionals are known keys in the table AND escape all str type comparison values
        allowed_operators = ['=', '==', '!=', '<>', '>', '<', '>=', '<=', '!<', '!>']
        conditional_strs = []
        for conditional in conditionals:
            if 'key' in conditional and 'operator' in conditional and 'comparison' in conditional:
                # Ensure that the given operator is allowed
                if conditional['operator'] in allowed_operators:
                    # Escape text type values
                    if type(conditional['comparison']) == str:
                        conditional_str = f'''{conditional['key']}{conditional['operator']}{repr(str(conditional['comparison']))}'''
                    elif type(conditional['comparison']) == int:
                        conditional_str = f'''{conditional['key']}{conditional['operator']}{int(conditional['comparison'])}'''
                    elif type(conditional['comparison']) == float:
                        conditional_str = f'''{conditional['key']}{conditional['operator']}{float(conditional['comparison'])}'''
                    # Save conditional string and break
                    conditional_strs.append(conditional_str)
                else:
                    print(f'''Conditional operator {conditional['operator']} not allowed''')
                    return []
            else:
                print('Incorrectly formatted conditional')
                return []
        # Ensure that the number of generated conditional strings is the same as the number of give conditional objects
        if len(conditionals) != len(conditional_strs):
            print('Not all conditionals are valid')
            return []
        return conditional_strs

    '''
    Create a table from a list of tuples of values
    '''
    def create_table(self, table, values, drop_existing=False):
        if drop_existing:
            # Drop the table if it exists; create a new one
            self.cur.execute(f'DROP TABLE IF EXISTS {table}')
        try:
            # Execute table creation with given values (nested list)
            self.cur.execute(f'''CREATE TABLE IF NOT EXISTS {table} ({', '.join([f'{value[0]} {value[1]}' for value in values])})''')
        except (sqlite3.OperationalError, sqlite3.ProgrammingError) as e:
            print(f'Sqlite3 Error when creating table {table}: {e}')
        # Commit and close connection
        self.conn.commit()
        self.conn.close

    '''
    Take a json object and insert it into the database
    '''
    def insert_doc(self, table, data):
        try:
            self.cur.execute(f'''INSERT INTO {table} VALUES ({','.join(['?' for i in range(len(data))])})''', list(data.values()))
        except (sqlite3.OperationalError, sqlite3.ProgrammingError) as e:
            print(f'ERROR with 1 document: {e}')
        # Commit and close connection
        self.conn.commit()
        self.conn.close

    '''
    Take a list of json objects and insert it into the database
    '''
    def insert_docs(self, table, datas):
        if len(datas) > 0:
            try:
                self.cur.executemany(f'''INSERT INTO {table} VALUES ({','.join(['?' for i in range(len(datas[0]))])})''', [list(data.values()) for data in datas])
            except (sqlite3.OperationalError, sqlite3.ProgrammingError) as e:
                print(f'ERROR with {len(datas)} documents: {e}')
            # Commit and close connection
            self.conn.commit()
            self.conn.close

    def update_doc(self, table, to_set, where):
        if len(to_set) > 0:
            # Prepare set string like filter strings
            to_set_strs = self.__prepare_conditional_str(table, to_set)
            if len(to_set_strs) > 0:
                if len(where) > 0 and type(where)==dict:
                    where_strs = self.__prepare_conditional_str(table, [where])
                    if len(where_strs) > 0:
                        try:
                            self.cur.execute(f'''Update {table} set {', '.join(to_set_strs)} where {where_strs[0]}''')
                        except (sqlite3.OperationalError, sqlite3.ProgrammingError) as e:
                            print(f'''Sqlite3 error when updating {', '.join(to_set_strs)} where {where_strs[0]} in {table}: {e}''')
                    else:
                        try:
                            self.cur.execute(f'''Update {table} set {to_set_strs[0]}''')
                        except (sqlite3.OperationalError, sqlite3.ProgrammingError) as e:
                            print(f'''Sqlite3 error when updating {to_set_strs[0]} in {table}: {e}''')
                    # Commit and close connection
                    self.conn.commit()
                    self.conn.close

    '''
    Query and return documents from a given table
    '''
    def get_docs(self, table, column='*', filters=[]):
        if len(filters) > 0:
            # Prepare filter strings
            filter_strs = self.__prepare_conditional_str(table, filters)
            if len(filter_strs) > 0:
                try:
                    self.cur.execute(f'''SELECT {column} FROM {table} WHERE {' AND '.join(filter_strs)}''')
                except (sqlite3.OperationalError, sqlite3.ProgrammingError) as e:
                    print(f'''Sqlite3 error when selecting max({column}) from table {table} where f{' AND '.join(filter_strs)}: {e}''')
                    docs = []
        else:
            try:
                self.cur.execute(f'SELECT {column} FROM {table}')
            except (sqlite3.OperationalError, sqlite3.ProgrammingError) as e:
                print(f'Sqlite3 error when selecting * from {table}: {e}')
                docs = []
        docs = self.cur.fetchall()
        # Commit and close connection
        self.conn.commit()
        self.conn.close
        return docs

    '''
    Query and return a max value of a column in a given table
    '''
    def get_max_val(self, table, column, filters=[]):
        if len(filters) > 0:
            # Prepare filter strings
            filter_strs = self.__prepare_conditional_str(table, filters)
            if len(filter_strs) > 0:
                try:
                    self.cur.execute(f'''SELECT max({column}) FROM {table} WHERE {' AND '.join(filter_strs)}''')
                except (sqlite3.OperationalError, sqlite3.ProgrammingError) as e:
                    print(f'''Sqlite3 error when selecting max({column}) from table {table} where f{' AND '.join(filter_strs)}: {e}''')
                    max = 0
        else:
            try:
                self.cur.execute(f'SELECT max({column}) FROM {table}')
            except (sqlite3.OperationalError, sqlite3.ProgrammingError) as e:
                print(f'Sqlite3 error when selecting max{column} from {table}: {e}')
                max = 0
        max_resp = self.cur.fetchone()
        if not max_resp:
            max = 0
        else:
            max = max_resp[0]
        # Commit and close connection
        self.conn.commit()
        self.conn.close
        return max

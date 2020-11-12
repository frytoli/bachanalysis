#!/usr/bin/env python

'''
Handle all data storage
'''

import sqlite3

class bachdb():
    def __init__(self, dbname):
        # Hardcode database name
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)
        self.cur = self.conn.cursor()

    def __prepare_filterstr(self, table, filters):
        # Ensure that all keys in the given filters are known keys in the table AND escape all str type comparison values
        allowed_operators = ['=', '==', '!=', '<>', '>', '<', '>=', '<=', '!<', '!>']
        filter_strs = []
        for filter in filters:
            if 'key' in filter and 'operator' in filter and 'comparison' in filter:
                # Ensure that the given operator is allowed
                if filter['operator'] in allowed_operators:
                    # Escape text type values
                    if type(filter['comparison']) == str:
                        filter_str = f'''{filter['key']}{filter['operator']}{repr(str(filter['comparison']))}'''
                    elif type(filter['comparison']) == int:
                        filter_str = f'''{filter['key']}{filter['operator']}{int(filter['comparison'])}'''
                    # Save conditional string and break
                    filter_strs.append(filter_str)
                else:
                    print(f'''Filter operator {filter['operator']} not allowed''')
                    return []
            else:
                print('Incorrectly formatted filter')
                return []
        # Ensure that the number of generated filter strings is the same as the number of give filter objects
        if len(filters) != len(filter_strs):
            print('Not all filters are valid')
            return []
        return filter_strs

    def create_table(self, table, values, drop_existing=False):
        if drop_existing:
            # Drop the table if it exists; create a new one
            self.cur.execute(f'DROP TABLE IF EXISTS {table}')
        try:
            # Execute table creation with given values (nested list)
            self.cur.execute(f'''CREATE TABLE IF NOT EXISTS {table} ({', '.join([f'{value[0]} {value[1]}' for value in values])})''')
        except sqlite3.OperationalError as e:
            print(f'Sqlite3 Error when creating table {table}: {e}')
        # Commit and close connection
        self.conn.commit()
        self.conn.close

    def insert_doc(self, table, doc):
        try:
            self.cur.execute(f'''INSERT INTO {table} VALUES ({','.join(['?' for i in range(len(doc))])})''', doc)
        except sqlite3.OperationalError as e:
            print(f'ERROR with 1 document: {e}')
        # Commit and close connection
        self.conn.commit()
        self.conn.close

    def insert_docs(self, table, docs):
        if len(docs) > 0:
            try:
                self.cur.executemany(f'''INSERT INTO {table} VALUES ({','.join(['?' for i in range(len(docs[0]))])})''', docs)
            except sqlite3.OperationalError as e:
                print(f'ERROR with {len(docs)} documents: {e}')
            # Commit and close connection
            self.conn.commit()
            self.conn.close

    def get_docs(self, table, column='*', filters=[]):
        if filters == {}:
            try:
                self.cur.execute(f'SELECT {column} FROM {table}')
            except sqlite3.OperationalError as e:
                print(f'Sqlite3 error when selecting * from {table}: {e}')
                docs = []
        else:
            # Prepare filter strings
            filter_strs = self.__prepare_filterstr(table, filters)
            if filter_strs != []:
                try:
                    self.cur.execute(f'''SELECT {column} FROM {table} WHERE {' AND '.join(filter_strs)}''')
                except sqlite3.OperationalError as e:
                    print(f'''Sqlite3 error when selecting max({column}) from table {table} where f{' AND '.join(filter_strs)}: {e}''')
                    docs = []
        if self.cur.fetchall():
            docs = self.cur.fetchall()
        else:
            docs = []
        # Commit and close connection
        self.conn.commit()
        self.conn.close
        return docs

    def get_max_val(self, table, column, filters=[]):
        if filters == {}:
            try:
                self.cur.execute(f'SELECT max({column}) FROM {table}')
            except sqlite3.OperationalError as e:
                print(f'Sqlite3 error when selecting max{column} from {table}: {e}')
                max = 0
        else:
            # Prepare filter strings
            filter_strs = self.__prepare_filterstr(table, filters)
            if len(filter_strs) > 0:
                try:
                    self.cur.execute(f'''SELECT max({column}) FROM {table} WHERE {' AND '.join(filter_strs)}''')
                except sqlite3.OperationalError as e:
                    print(f'''Sqlite3 error when selecting max({column}) from table {table} where f{' AND '.join(filter_strs)}: {e}''')
                    max = 0
        max = self.cur.fetchone()[0]
        if not max:
            max = 0
        # Commit and close connection
        self.conn.commit()
        self.conn.close
        return max

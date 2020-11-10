#!/usr/bin/env python

import sqlite3

class bachdb():
    def __init__(self, dbname):
        # Hardcode database name
        self.dbname = dbname
        # Data model references for all tables
        self.tables = {
            'ds1': {
                'name': 'ds1',
                'keys': [('season', 'integer'), ('original_run', 'text'), ('bachelor', 'text'), ('winner', 'text'), ('runnersup', 'text'), ('proposal', 'text'), ('still_together', 'text'), ('relationship_notes', 'text')]
            },
            'ds2': {
                'name': 'ds2',
                'keys': [('season', 'integer'), ('original_run', 'text'), ('bachelorette', 'text'), ('winner', 'text'), ('runnerup', 'text'), ('proposal', 'text'), ('still_together', 'text'), ('relationship_notes', 'text')]
            },
            'ds3': {
                'name': 'ds3',
                'keys': [('name', 'text'), ('age', 'integer'), ('hometown', 'text'), ('occupation', 'text'), ('eliminated', 'text'), ('season', 'integer'), ('place', 'integer')]
            },
            'ds4': {
                'name': 'ds4',
                'keys': [('name', 'text'), ('age', 'integer'), ('hometown', 'text'), ('occupation', 'text'), ('eliminated', 'text'), ('season', 'integer'), ('place', 'integer')]
            },
            'ds5': {
                'name': 'ds5',
                'keys': [('photo', 'text'), ('name', 'text'), ('born', 'text'), ('hometown', 'text'), ('occupation', 'text'), ('seasons', 'text'), ('height', 'text')]
            },
        }
        self.conn = sqlite3.connect(dbname)
        self.cur = self.conn.cursor()
        # Create all tables if they do not already exist
        for table in self.tables:
            self.create_table(table)

    def __prepare_filterstr(self, table, filters):
        # Ensure that all keys in the given filters are known keys in the table AND escape all str type comparison values
        allowed_operators = ['=', '==', '!=', '<>', '>', '<', '>=', '<=', '!<', '!>']
        filter_strs = []
        for filter in filters:
            if 'key' in filter and 'operator' in filter and 'comparison' in filter:
                # Ensure that the given operator is allowed
                if filter['operator'] in allowed_operators:
                    for keypair in self.tables[table]['keys']:
                        # Find filter key in data model
                        if filter['key'] == keypair[0]:
                            # Escape text type values
                            if keypair[1] == 'text':
                                filter_str = f'''{filter['key']}{filter['operator']}{repr(str(filter['comparison']))}'''
                            else:
                                filter_str = f'''{filter['key']}{filter['operator']}{int(filter['comparison'])}'''
                            # Save conditional string and break
                            filter_strs.append(filter_str)
                            break
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

    def __prepare_doc(self, table, raw_doc):
        # Prepare a document according to the data model specific to the given table
        doc = [] # Order of values matters
        for keypair in self.tables[table]['keys']:
            key, type = keypair[0], keypair[1]
            if key in raw_doc:
                doc.append(raw_doc[key])
            else:
                if type == 'text':
                    doc.append('')
                elif type == 'integer':
                    doc.append(0)
        return doc

    def create_table(self, table, drop_existing=False):
        if drop_existing:
            # Drop the table if it exists; create a new one
            self.cur.execute(f'DROP TABLE IF EXISTS {table}')
        try:
            # Execute table creation with provided headers
            self.cur.execute(f'''CREATE TABLE IF NOT EXISTS {table} ({', '.join([f'{pair[0]} {pair[1]}' for pair in self.tables[table]['keys']])})''')
        except sqlite3.OperationalError as e:
            print(f'Sqlite3 Error when creating table {table}: {e}')
        # Commit and close connection
        self.conn.commit()
        self.conn.close

    def insert_doc(self, table, raw_doc):
        # Check that the table is known
        if table not in self.tables:
            print(f'No table {table} is known')
        else:
            # Prepare a document according to the data model specific to the given table
            doc = self.__prepare_doc(table, raw_doc)
            try:
                self.cur.execute(f'''INSERT INTO {table} VALUES ({','.join(['?' for i in range(len(self.tables[table]['keys']))])})''', doc)
            except Exception as e:
                print(f'ERROR with {doc}: {e}')
            # Commit and close connection
            self.conn.commit()
            self.conn.close

    def insert_docs(self, table, raw_docs):
        # Check that the table is known
        if table not in self.tables:
            print(f'No table {table} is known')
        else:
            # Prepare all documents according to the data model specific to the given table
            docs = [self.__prepare_doc(table, raw_doc) for raw_doc in raw_docs]
            try:
                self.cur.executemany(f'''INSERT INTO {table} VALUES ({','.join(['?' for i in range(len(self.tables[table]['keys']))])})''', docs)
            except Exception as e:
                print(f'ERROR with {len(docs)} documents: {e}')
            # Commit and close connection
            self.conn.commit()
            self.conn.close

    def get_docs(self, table, filters={}, column='*'):
        # Check that the table is known
        if table not in self.tables:
            print(f'No table {table} is known')
            return []
        else:
            if filters == {}:
                try:
                    self.cur.execute(f'SELECT {column} FROM {table}')
                except sqlite3.OperationalError as e:
                    print(f'Sqlite3 error when selecting * from {table}: {e}')
                    return []
            else:
                # Prepare filter strings
                filter_strs = self.__prepare_filterstr(table, filters)
                if filter_strs != []:
                    try:
                        self.cur.execute(f'''SELECT {column} FROM {table} WHERE {' AND '.join(filter_strs)}''')
                    except sqlite3.OperationalError as e:
                        print(f'''Sqlite3 error when selecting max({column}) from table {table} where f{' AND '.join(filter_strs)}: {e}''')
                        return []
            # Commit and close connection
            self.conn.commit()
            self.conn.close
            return self.cur.fetchall()

    def get_max_val(self, table, column, filters={}):
        # Check that the table is known
        if table not in self.tables:
            print(f'No table {table} is known')
            return 0
        else:
            if filters == {}:
                try:
                    self.cur.execute(f'SELECT max({column}) FROM {table}')
                except sqlite3.OperationalError as e:
                    print(f'Sqlite3 error when selecting max{column} from {table}: {e}')
                    return 0
            else:
                # Prepare filter strings
                filter_strs = self.__prepare_filterstr(table, filters)
                if filter_strs != []:
                    try:
                        self.cur.execute(f'''SELECT max({column}) FROM {table} WHERE {' AND '.join(filter_strs)}''')
                    except sqlite3.OperationalError as e:
                        print(f'''Sqlite3 error when selecting max({column}) from table {table} where f{' AND '.join(filter_strs)}: {e}''')
                        return 0
            # Commit and close connection
            self.conn.commit()
            self.conn.close
            return self.cur.fetchone()[0]

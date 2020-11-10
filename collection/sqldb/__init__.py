#!/usr/bin/env python

import sqlite3

class db():
    def __init__(self, dbname):
        self.dbname = dbname
        if dbname.lower().endswith('.db'):
            self.conn = sqlite3.connect(dbname)
            self.cur = self.conn.cursor()
        else:
            print('Incorrect dbname extension')

    def craft_headers(self, record):
        headers = []
        for key, value in record.items():
            if not value:
                headers.append(f'{key} null')
            elif type(value) == str:
                headers.append(f'{key} text')
            elif type(value) == int:
                headers.append(f'{key} integer')
            elif type(value) == float:
                headers.append(f'{key} real')
            else:
                headers.append(f'{key} blob')
                headers[key] = 'blob'
        return headers

    def create_table(self, table, headers, drop_existing=False):
        if drop_existing:
            # Drop the table if it exists; create a new one
            self.cur.execute(f'DROP TABLE IF EXISTS {table}')
        try:
            # Execute table creation with provided headers
            self.cur.execute(f'''CREATE TABLE IF NOT EXISTS {table} ({', '.join([header for header in headers])})''')
        except sqlite3.OperationalError as e:
            print(f'Sqlite3 Error when creating table {table}: {e}')
        # Commit and close connection
        self.conn.commit()
        self.conn.close

    def insert_doc(self, table, doc):
        self.cur.execute(f'''INSERT INTO {table} VALUES ({','.join(['?' for i in range(len(doc))])})''', list(doc.values()))
        # Commit and close connection
        self.conn.commit()
        self.conn.close

    def insert_docs(self, table, docs):
        self.cur.executemany(f'''INSERT INTO {table} VALUES ({','.join(['?' for i in range(len(docs[0]))])})''', [list(doc.values()) for doc in docs])
        # Commit and close connection
        self.conn.commit()
        self.conn.close

    def get_docs(self, table, filters={}, column='*'):
        if filters == {}:
            self.cur.execute(f'SELECT {column} FROM {table}')
        else:
            filter_str = ' AND '.join([f'''{filter['key']}{filter['operator']}{filter['comparison']}''' for filter in filters])
            self.cur.execute(f'SELECT {column} FROM {table} WHERE {filter_str}')
        return self.cur.fetchall()
        # Commit and close connection
        self.conn.commit()
        self.conn.close

    def get_max_val(self, table, column, filters={}):
        if filters == {}:
            try:
                self.cur.execute(f'SELECT max({column}) FROM {table}')
            except sqlite3.OperationalError as e:
                print(f'Sqlite3 Error: {e}. Returning maximum value of 0.')
                return 0
        else:
            try:
                filter_str = ' AND '.join([f'''{filter['key']}{filter['operator']}{filter['comparison']}''' for filter in filters])
                self.cur.execute(f'SELECT max({column}) FROM {table} WHERE {filter_str}')
            except sqlite3.OperationalError as e:
                print(f'Sqlite3 Error: {e}. Returning maximum value of 0.')
                return 0
        return self.cur.fetchone()[0]
        # Commit and close connection
        self.conn.commit()
        self.conn.close

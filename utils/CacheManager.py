import sqlite3
import tempfile
import os
import urllib.request
import ast
import json

'''
    This class manages local cache
'''

class CacheManager:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.db_name = "AC_local_cache.db"
        self.db_path = os.path.join(self.temp_dir, self.db_name)
        self.database = None
        self.is_dev = False
        self.init_db()

    def dev_print(self, content):
        if self.is_dev:
            print(content)

    def init_db(self):
        if not os.path.isfile(self.db_path):
            try:
                c = self.get_db().cursor()
                c.execute("CREATE TABLE IF NOT EXISTS local_cache (key TEXT NOT NULL PRIMARY KEY, value BLOB)")
                self.get_db().commit()
                c.close()
                self.dev_print("Success when initializing local cache")
            except sqlite3.Error:
                self.dev_print("Something failed when initializing local cache")

    def get_db(self):
        if not self.database:
            self.database = sqlite3.connect(self.db_path)
        return self.database

    def close_db(self):
        self.database.close()
        self.database = None

    def put_object(self, key, value):
        c = self.get_db().cursor()
        c.execute("INSERT OR REPLACE INTO local_cache VALUES (?,?)", (str(key), json.dumps(value,)))
        self.get_db().commit()
        c.close()

    def put_string(self, key, value):
        c = self.get_db().cursor()
        c.execute("INSERT OR REPLACE INTO local_cache VALUES (?,?)", (str(key), (sqlite3.Binary(value),)))
        self.get_db().commit()
        c.close()

    def put_buffer(self, key, value):
        c = self.get_db().cursor()
        c.execute("INSERT OR REPLACE INTO local_cache VALUES (?,?)", (str(key), value,))
        self.get_db().commit()
        c.close()

    def get(self, key):
        c = self.get_db().cursor()
        r = None
        for row in c.execute("SELECT value FROM local_cache WHERE key = ?", (str(key),)):
            r = row[0]
        c.close()
        return r



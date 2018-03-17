import sqlite3
import tempfile
import os
import urllib.request
import ast

'''
    This class manages local cache
'''


class CacheManager:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.db_name = "AC_local_cache.db"
        self.temp_path = os.path.join(self.temp_dir, self.db_name)
        self.database = sqlite3.connect(self.temp_path)
        self.is_dev = False

    def dev_print(self, content):
        if self.is_dev:
            print(content)

    def open_db(self):
        self.database = sqlite3.connect(self.temp_path)
        self.dev_print("_____________________\n")
        self.dev_print("Database opened")

    def close_db(self):
        self.database.close()
        self.database = None
        self.dev_print("Database closed")
        self.dev_print("_____________________")

    def format_json_to_insert(self, my_list):
        # The json library of Python requires double quotes instead of simple ones
        r = str(my_list)
        r = r.replace("'", "\"")
        return r

    def format_json_after_fetch(self, string):
        return ast.literal_eval(string)

    def init_db(self):
        try:
            c = self.database.cursor()

            c.execute("CREATE TABLE IF NOT EXISTS local_cache (url TEXT NOT NULL PRIMARY KEY, name TEXT, schema_hash TEXT, schema TEXT, img_hash TEXT, img BLOB)")

            self.database.commit()
            c.close()
            self.dev_print("Success when initializing local cache")
        except sqlite3.Error:
            self.dev_print("Something failed when initializing local cache")

    def verify_existence(self, column_name, column_to_verify):
        c = self.database.cursor()
        c.execute("SELECT * FROM local_cache WHERE " + column_name + "=? LIMIT 1", (column_to_verify,))
        exists = c.fetchone() is not None
        c.close()
        return exists

    def verify_row_exists(self, url):
        return self.verify_existence("url", url)

    def verify_schema_hash_changed(self, schema_hash, cache):
        if cache:
            return not self.verify_existence("schema_hash", schema_hash)
        else:
            return True

    def verify_img_hash_changed(self, img_hash, cache):
        if cache:
            return not self.verify_existence("img_hash", img_hash)
        else:
            return True

    def add_row(self, url, name, schema_hash, schema, img_hash, img_url):
        schema = self.format_json_to_insert(schema)
        img_url += "?token=" + os.environ["AMIGOCLOUD_API_KEY"]
        img = urllib.request.urlopen(img_url).read()
        values = (url, name, schema_hash, schema, img_hash, img)
        c = self.database.cursor()
        c.execute("INSERT OR REPLACE INTO local_cache VALUES (?,?,?,?,?,?)", values)
        self.database.commit()
        c.close()
        self.dev_print("Row added: " + name)

    def fetch_value(self, value, url):
        c = self.database.cursor()
        r = None
        for output in c.execute("SELECT " + value + " FROM local_cache WHERE url = ? LIMIT 1", (url,)):
            r = output[0]
        c.close()
        return r

    def update_value(self, column, value, url):
        c = self.database.cursor()
        c.execute("UPDATE local_cache SET " + str(column) + " = ? WHERE url = ?", (value, url))
        c.close()
        self.dev_print("Row updated -> url: [" + url + "] @ [" + column + "]")

    def update_schema(self, schema_hash, schema, url):
        schema = self.format_json_to_insert(schema)
        values = (schema_hash, schema, url)
        c = self.database.cursor()
        c.execute("UPDATE local_cache SET schema_hash = ?, schema = ? WHERE url = ?", values)
        c.close()
        self.dev_print("Row updated -> url: [" + url + "] @ schema && schema_hash")

    def update_img(self, img_hash, img_url, url):
        img_url += "?token=" + os.environ["AMIGOCLOUD_API_KEY"]
        img = urllib.request.urlopen(img_url).read()
        c = self.database.cursor()
        values = (img_hash, img, url)
        c.execute("UPDATE local_cache SET img_hash = ?, img = ? WHERE url = ?", values)
        c.close()
        self.dev_print("Row updated -> url: [" + url + "] @ img && img_hash")

    def fetch_img(self, url):
        return self.fetch_value("img", url)

    def fetch_schema(self, usr_id, project_id, dataset_id):
        url = "https://www.amigocloud.com/api/v1/users/" + str(usr_id) + "/projects/" + str(project_id) + "/datasets/" + str(dataset_id)
        r = self.fetch_value("schema", url)
        r = self.format_json_after_fetch(r)
        return r


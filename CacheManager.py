import sqlite3
import tempfile
import os
import urllib.request

'''
    This class manages local cache
'''


class CacheManager:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.db_name = "amigocloud_local_db.db"
        self.temp_path = os.path.join(self.temp_dir, self.db_name)
        self.conn = sqlite3.connect(self.temp_path)
        self.is_dev = False

    def dev_print(self, content):
        if self.is_dev:
            print(content)

    def close_conn(self):
        self.conn.close()

    def init_db(self):
        try:
            c = self.conn.cursor()

            '''
                Use these in the future, when the hash issues have been solved
                and the endpoint is improved.
                We'll just cache images because everything else is irrelevant right now.
                For this reason, some of the functions are not usable
            '''
            # c.execute(
            #     "CREATE TABLE IF NOT EXISTS projects (p_id INTEGER, p_name TEXT, p_hash TEXT, p_image BLOB, p_img_hash TEXT, p_updated INTEGER)")
            # c.execute(
            #     "CREATE TABLE IF NOT EXISTS datasets (ds_p_url TEXT, ds_url TEXT PRIMARY KEY, ds_id INTEGER, ds_name TEXT, ds_hash TEXT, ds_image BLOB, ds_img_hash TEXT)")
            c.execute("CREATE TABLE IF NOT EXISTS projects (p_url TEXT, p_id INTEGER, p_hash TEXT, p_img BLOB)")
            c.execute("CREATE TABLE IF NOT EXISTS datasets (ds_url TEXT, ds_p_url TEXT, ds_id INTEGER, ds_hash TEXT, ds_img BLOB)")
            self.conn.commit()
            c.close()
            self.dev_print("Success when initializing tables for images")
        except sqlite3.Error:
            self.dev_print("Something failed when initializing tables for images")

    def verify_existence(self, table, column_name, column_to_verify):
        c = self.conn.cursor()
        c.execute("SELECT * FROM " + table + " WHERE " + column_name + "=? LIMIT 1", (column_to_verify,))
        exists = c.fetchone() is not None
        c.close()
        return exists

    def verify_project_exists(self, p_id):
        return self.verify_existence("projects", "p_url", p_id)

    def verify_dataset_exists(self, ds_id):
        return self.verify_existence("datasets", "ds_url", ds_id)

    def verify_project_hash_changed(self, p_hash):
        return not self.verify_existence("projects", "p_hash", p_hash)

    def verify_dataset_hash_changed(self, ds_hash):
        return not self.verify_existence("datasets", "ds_hash", ds_hash)

    def verify_project_image_hash_changed(self, p_img_hash):
        return not self.verify_existence("projects", "p_img_hash", p_img_hash)

    def verify_dataset_image_hash_changed(self, ds_img_hash):
        return not self.verify_existence("datasets", "ds_img_hash", ds_img_hash)

    def set_project_updated(self, p_url, p_updated):
        c = self.conn.cursor()

        c.execute("UPDATE projects SET p_updated = ? WHERE p_url = ?", (p_updated, p_url))
        self.conn.commit()
        c.close()

    def check_project_updated(self, ds_p_url):
        c = self.conn.cursor()
        r = None
        for project in c.execute("SELECT * FROM projects WHERE p_url = ? LIMIT 1", (ds_p_url,)):
            r = project[6]
        c.close()
        return r

    def temp_insert_new_project(self, p_url, p_id, p_hash, p_img_url):
        c = self.conn.cursor()

        p_img_url += '?token=' + os.environ['AMIGOCLOUD_API_KEY']
        img_data = urllib.request.urlopen(p_img_url).read()
        new_values = (p_url, p_id, p_hash, img_data)
        c.execute("INSERT OR REPLACE INTO projects VALUES (?,?,?,?)", new_values)
        self.conn.commit()
        c.close()

    def temp_insert_new_dataset(self, ds_url, ds_p_url, ds_id, ds_hash, ds_img_url):
        c = self.conn.cursor()

        ds_img_url += '?token=' + os.environ['AMIGOCLOUD_API_KEY']
        img_data = urllib.request.urlopen(ds_img_url).read()
        new_values = (ds_url, ds_p_url, ds_id, ds_hash, img_data)
        c.execute("INSERT OR REPLACE INTO datasets VALUES (?,?,?,?,?)", new_values)
        self.conn.commit()
        c.close()

    def temp_update_project(self, p_id, p_hash, p_img_url):
        c = self.conn.cursor()

        p_img_url += '?token=' + os.environ['AMIGOCLOUD_API_KEY']
        img_data = urllib.request.urlopen(p_img_url).read()
        updated_values = (p_hash, img_data, p_id)
        c.execute("UPDATE projects SET p_hash = ?, p_img = ? WHERE p_id = ?", updated_values)
        self.conn.commit()
        c.close()

    def temp_update_dataset(self, ds_id, ds_hash, ds_img_url):
        c = self.conn.cursor()

        ds_img_url += '?token=' + os.environ['AMIGOCLOUD_API_KEY']
        img_data = urllib.request.urlopen(ds_img_url).read()
        updated_values = (ds_hash, img_data, ds_id)
        c.execute("UPDATE datasets SET ds_hash = ?, ds_img = ? WHERE ds_id = ?", updated_values)
        self.conn.commit()
        c.close()

    def temp_get_project_image(self, p_id):
        c = self.conn.cursor()
        row = c.execute("SELECT * FROM projects WHERE p_id = ?", (p_id,))
        r = None
        for load in row:
            r = load[3]

        c.close()
        return r

    def temp_get_dataset_image(self, ds_id):
        c = self.conn.cursor()
        row = c.execute("SELECT * FROM datasets WHERE ds_id = ?", (ds_id,))
        r = None
        for load in row:
            r = load[4]

        c.close()
        return r

    def insert_new_project(self, p_url, p_id, p_name, p_hash, p_img_url, p_img_hash, p_updated):
        c = self.conn.cursor()

        p_img_url += '?token=' + os.environ['AMIGOCLOUD_API_KEY']
        img_data = urllib.request.urlopen(p_img_url).read()
        new_values = (p_url, p_id, p_name, p_hash, img_data, p_img_hash, p_updated)
        c.execute("INSERT OR IGNORE INTO projects VALUES(?,?,?,?,?,?,?)", new_values)
        self.conn.commit()

        c.close()

    def insert_new_dataset(self, ds_p_url, ds_url, ds_id, ds_name, ds_hash, ds_img_url, ds_img_hash):
        c = self.conn.cursor()

        ds_img_url += '?token=' + os.environ['AMIGOCLOUD_API_KEY']
        img_data = urllib.request.urlopen(ds_img_url).read()
        new_values = (ds_p_url, ds_url, ds_id, ds_name, ds_hash, img_data, ds_img_hash)
        c.execute("INSERT OR IGNORE INTO datasets VALUES(?,?,?,?,?,?,?)", new_values)
        self.conn.commit()

        c.close()

    def update_project_all(self, p_url, p_hash, p_name, p_img_url, p_img_hash):
        c = self.conn.cursor()

        p_img_url += '?token=' + os.environ['AMIGOCLOUD_API_KEY']
        img_data = urllib.request.urlopen(p_img_url).read()
        updated_values = (p_name, p_hash, img_data, p_img_hash, p_url)
        c.execute(
            "UPDATE projects SET p_name = ?, p_hash = ?,p_image = ?, p_img_hash = ? WHERE p_url = ?",
            updated_values)
        self.conn.commit()
        c.close()

    def update_dataset_all(self, ds_url, ds_hash, ds_name, ds_img_url, ds_img_hash):
        c = self.conn.cursor()
        ds_img_url += '?token=' + os.environ['AMIGOCLOUD_API_KEY']
        img_data = urllib.request.urlopen(ds_img_url).read()
        updated_values = (ds_name, ds_hash, img_data, ds_img_hash, ds_url)
        c.execute(
            "UPDATE datasets SET ds_name = ?, ds_hash = ?,ds_image = ?, ds_img_hash = ? WHERE ds_url = ?",
            updated_values)
        self.conn.commit()
        c.close()

    def update_project_name(self, p_url, p_hash, p_name):
        c = self.conn.cursor()
        updated_values = (p_name, p_hash, p_url)

        c.execute("UPDATE projects SET p_name = ?, p_hash = ? WHERE p_url = ?", updated_values)
        self.conn.commit()
        c.close()

    def update_dataset_name(self, ds_url, ds_hash, ds_name):
        c = self.conn.cursor()
        updated_values = (ds_name, ds_hash, ds_url)

        c.execute("UPDATE datasets SET ds_name = ?, ds_hash = ?, WHERE ds_url = ?", updated_values)
        self.conn.commit()
        c.close()

    def load_urls_from_projects_local(self):
        c = self.conn.cursor()
        r = []
        for url in c.execute("SELECT * FROM projects"):
            r.append(url[0])

        c.close()
        return r

    def load_urls_from_datasets_local(self, ds_p_url):
        c = self.conn.cursor()
        r = []
        for url in c.execute("SELECT * FROM datasets WHERE ds_p_url = ?", (ds_p_url,)):
            r.append(url[0])

        c.close()
        return r

    def load_from_projects(self, p_id):
        c = self.conn.cursor()
        r = None
        for load in c.execute("SELECT * FROM projects WHERE p_url = ?", (p_id,)):
            r = load
        c.close()
        return r

    def load_from_datasets(self, ds_id):
        c = self.conn.cursor()
        r = None
        for load in c.execute("SELECT * FROM datasets WHERE ds_url = ?", (ds_id,)):
            r = load
        c.close()
        return r

    def delete_project_local(self, p_id):
        c = self.conn.cursor()
        c.execute("DELETE FROM projects WHERE p_id = ?", (p_id,))
        self.conn.commit()
        c.close()

    def delete_dataset_local(self, ds_id):
        c = self.conn.cursor()
        c.execute("DELETE FROM datasets WHERE ds_id = ?", (ds_id,))
        self.conn.commit()
        c.close()

    def project_trashcan(self, remote, local):
        to_delete = []
        deleted = 0
        for url in local:
            if url not in remote:
                to_delete.append(url)

        for row in to_delete:
            self.delete_project_local(row)
            deleted += 1
        self.dev_print("___________________________________________________\n")
        self.dev_print("[" + str(deleted) + "] projects deleted from local")

    def dataset_trashcan(self, remote, local):
        to_delete = []
        deleted = 0
        for url in local:
            if url not in remote:
                to_delete.append(url)
        self.dev_print(to_delete)
        for row in to_delete:
            self.delete_dataset_local(row)
            deleted += 1
        self.dev_print("___________________________________________________\n")
        self.dev_print("[" + str(deleted) + "] datasets deleted from local")

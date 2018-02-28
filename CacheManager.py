import sqlite3
import tempfile
import os
import urllib.request

class CacheManager():
    def __init__(self):
        self.tempDir = tempfile.gettempdir()
        self.dbName = "amigocloud_local_db.db"
        self.isDev = False

    def devPrint(self,content):
        if self.isDev == True:
            print(content)

    def openConn(self):
        tempPath = os.path.join(self.tempDir,self.dbName)
        conn = sqlite3.connect(tempPath)
        return conn

    def closeConn(self,cursor):
        cursor.close()

    def initializeDB(self):
        try:
            conn = self.openConn()
            c = conn.cursor()
            c.execute(
                "CREATE TABLE IF NOT EXISTS projects (p_url TEXT PRIMARY KEY, p_id INTEGER, p_name TEXT, p_hash TEXT, p_image BLOB, p_img_hash TEXT, p_updated INTEGER)")
            c.execute(
                "CREATE TABLE IF NOT EXISTS datasets (ds_p_url TEXT, ds_url TEXT PRIMARY KEY, ds_id INTEGER, ds_name TEXT, ds_hash TEXT, ds_image BLOB, ds_img_hash TEXT)")
            self.closeConn(c)
            self.devPrint("Success when initializing tables for images")
        except Exception:
            self.devPrint("Something failed when initializing tables for images")

    def verifyExistence(self, table, columnName, columnToVerify):
        conn = self.openConn()
        c = conn.cursor()
        c.execute("SELECT * FROM " + table + " WHERE "+ columnName +"=? LIMIT 1", (columnToVerify,))
        exists = c.fetchone() is not None
        self.closeConn(c)
        return exists

    def verifyProjectExists(self, p_url):
        return self.verifyExistence("projects","p_url",p_url)

    def verifyDatasetExists(self,ds_url):
        return self.verifyExistence("datasets","ds_url",ds_url)

    def verifyProjectHashChanged(self, p_hash):
        return not self.verifyExistence("projects","p_hash",p_hash)

    def verifyDatasetHashChanged(self,ds_hash):
        return not self.verifyExistence("datasets","ds_hash",ds_hash)

    def verifyProjectImageHashChanged(self, p_img_hash):
        return not self.verifyExistence("projects","p_img_hash",p_img_hash)

    def verifyDatasetImageHashChanged(self, ds_img_hash):
        return not self.verifyExistence("datasets","ds_img_hash",ds_img_hash)

    def setProjectUpdated(self,p_url,p_updated):
        conn = self.openConn()
        c = conn.cursor()

        c.execute("UPDATE projects SET p_updated = ? WHERE p_url = ?",(p_updated,p_url))
        conn.commit()
        self.closeConn(c)

    def checkProjectUpdated(self, ds_p_url):
        conn = self.openConn()
        c = conn.cursor()
        r = None
        for project in c.execute("SELECT * FROM projects WHERE p_url = ? LIMIT 1",(ds_p_url,)):
            r = project[6]
        self.closeConn(c)
        return r


    def insertNewProject(self, p_url, p_id, p_name, p_hash, p_img_url, p_img_hash, p_updated):
        conn = self.openConn()
        c = conn.cursor()

        p_img_url += '?token=' + os.environ['AMIGOCLOUD_API_KEY']
        img_data = urllib.request.urlopen(p_img_url).read()
        newValues = (p_url, p_id, p_name, p_hash, img_data, p_img_hash, p_updated)
        c.execute("INSERT OR IGNORE INTO projects VALUES(?,?,?,?,?,?,?)", newValues)
        conn.commit()

        self.closeConn(c)

    def insertNewDataset(self,ds_p_url,ds_url,ds_id,ds_name,ds_hash,ds_img_url,ds_img_hash):
        conn = self.openConn()
        c = conn.cursor()

        ds_img_url += '?token=' + os.environ['AMIGOCLOUD_API_KEY']
        img_data = urllib.request.urlopen(ds_img_url).read()
        newValues = (ds_p_url, ds_url, ds_id, ds_name, ds_hash, img_data, ds_img_hash)
        c.execute("INSERT OR IGNORE INTO datasets VALUES(?,?,?,?,?,?,?)", newValues)
        conn.commit()

        self.closeConn(c)

    def updateProjectAll(self, p_url, p_hash, p_name, p_img_url, p_img_hash):
        conn = self.openConn()
        c = conn.cursor()
        p_img_url += '?token=' + os.environ['AMIGOCLOUD_API_KEY']
        img_data = urllib.request.urlopen(p_img_url).read()
        updatedValues = (p_name,p_hash, img_data,p_img_hash,p_url)
        c.execute("UPDATE projects SET p_name = ?, p_hash = ?,p_image = ?, p_img_hash = ? WHERE p_url = ?", updatedValues)
        conn.commit()
        self.closeConn(c)

    def updateDatasetAll(self, ds_url, ds_hash, ds_name, ds_img_url, ds_img_hash):
        conn = self.openConn()
        c = conn.cursor()
        ds_img_url += '?token=' + os.environ['AMIGOCLOUD_API_KEY']
        img_data = urllib.request.urlopen(ds_img_url).read()
        updatedValues = (ds_name,ds_hash, img_data,ds_img_hash,ds_url)
        c.execute("UPDATE datasets SET ds_name = ?, ds_hash = ?,ds_image = ?, ds_img_hash = ? WHERE ds_url = ?",updatedValues)
        conn.commit()
        self.closeConn(c)

    def updateProjectName(self, p_url, p_hash, p_name):
        conn = self.openConn()
        c = conn.cursor()
        updated_values = (p_name, p_hash, p_url)

        c.execute("UPDATE projects SET p_name = ?, p_hash = ? WHERE p_url = ?", updated_values)
        conn.commit()
        self.closeConn(c)

    def updateDatasetname(self, ds_url, ds_hash, ds_name):
        conn = self.openConn()
        c = conn.cursor()
        updatedValues = (ds_name, ds_hash, ds_url)

        c.execute("UPDATE datasets SET ds_name = ?, ds_hash = ?, WHERE ds_url = ?",updatedValues)
        conn.commit()
        self.closeConn(c)

    def loadAllUrlsFromProjectsLocal(self):
        conn = self.openConn()
        c = conn.cursor()
        r = []
        for url in c.execute("SELECT * FROM projects"):
            r.append(url[0])

        return r

    def loadAllUrlsFromDatasetsLocal(self,ds_p_url):
        conn = self.openConn()
        c = conn.cursor()
        r = []
        for url in c.execute("SELECT * FROM datasets WHERE ds_p_url = ?",(ds_p_url,)):
            r.append(url[1])
        return r

    def loadFromProjects(self,p_url):
        conn = self.openConn()
        c = conn.cursor()
        r = None
        for load in c.execute("SELECT * FROM projects WHERE p_url = ?", (p_url,)):
            r = load
        self.closeConn(c)
        return r

    def loadFromDatasets(self,ds_url):
        conn = self.openConn()
        c = conn.cursor()
        r = None
        for load in c.execute("SELECT * FROM datasets WHERE ds_url = ?", (ds_url,)):
            r = load
        self.closeConn(c)
        return r

    def deleteLocalProject(self,p_url):
        conn = self.openConn()
        c = conn.cursor()
        c.execute("DELETE FROM projects WHERE p_url = ?",(p_url,))
        conn.commit()
        self.closeConn(c)

    def deleteLocalDataset(self,ds_url):
        conn = self.openConn()
        c = conn.cursor()
        c.execute("DELETE FROM datasets WHERE ds_url = ?",(ds_url,))
        conn.commit()
        self.closeConn(c)

    def projectTrashcan(self,remote,local):
        toDelete = []
        deleted = 0
        for url in local:
            if url not in remote:
                toDelete.append(url)

        for row in toDelete:
            self.deleteLocalProject(row)
            deleted += 1
        self.devPrint("___________________________________________________\n")
        self.devPrint("[" + str(deleted) + "] projects deleted from local")

    def datasetTrashcan(self,remote,local):
        toDelete = []
        deleted = 0
        for url in local:
            if url not in remote:
                toDelete.append(url)
        self.devPrint(toDelete)
        for row in toDelete:
            self.deleteLocalDataset(row)
            deleted += 1
        self.devPrint("___________________________________________________\n")
        self.devPrint("[" + str(deleted) + "] datasets deleted from local")
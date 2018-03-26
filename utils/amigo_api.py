import base64
import json
import os
import urllib.request
import requests

from .amigocloud import AmigoCloud
from .CacheManager import CacheManager
from io import BytesIO

class AmigoAPI:
    def __init__(self, token):
        try:
            self.token = os.environ['AMIGOCLOUD_API_KEY']
        except:
            self.token = token

        self.base_url = 'https://www.amigocloud.com'
        self.ac = AmigoCloud(token=self.token, base_url=self.base_url)
        self.mixpanel_token = self.fetch_mixpanel_token()
        self.plugin_version = "0.9"
        self.cm = CacheManager()

    def set_token(self, token):
        self.token = token
        self.ac = AmigoCloud(token=self.token, base_url=self.base_url)
        self.mixpanel_token = self.fetch_mixpanel_token()

    def fetch(self, uri, use_cache):
        if use_cache:
            resp = self.cm.get(uri)
        else:
            resp = None
        if not resp or not use_cache:
            resp = self.ac.get(uri)
            self.cm.put_object(uri, resp)
        return resp

    def fetch_project_list(self, use_cache):
        uri = self.base_url + '/api/v1/me/projects?summary'
        resp = self.fetch(uri, use_cache)
        if 'results' in resp:
            return resp['results']
        else:
            return []

    def fetch_dataset_list(self, project_id):
        dataset_url = self.base_url + '/api/v1/users/0/projects/' + project_id + '/datasets?summary'
        resp = self.ac.get(dataset_url)
        if 'results' in resp:
            return resp['results']
        else:
            return []

    def fetch_dataset_relations(self, project_id, dataset_id):  # Queries the relationships of a dataset
        relations_url = self.base_url + '/api/v1/users/0/projects/' + project_id + '/datasets/' + dataset_id + '/relationships/'
        resp = self.ac.get(relations_url)
        if 'results' in resp:
            return resp['results']
        else:
            return []

    def fetch_schema(self, usr_id, project_id, dataset_id, use_cache):
        url = self.base_url + "/api/v1/users/" + str(usr_id) + "/projects/" + str(project_id) + "/datasets/" + str(dataset_id) + "/schema"
        r = self.fetch(url, use_cache)
        return r['schema']

    def get_user_name(self):
        url = "https://www.amigocloud.com/api/v1/me"
        resp = self.ac.get(url)
        if 'email' in resp and 'first_name' in resp and 'last_name' in resp:
            return resp['first_name'] + ' ' + resp['last_name'] + ' <' + resp['email'] + '>'
        else:
            return ''

    def get_user_id(self):
        url = "https://www.amigocloud.com/api/v1/me"
        resp = self.ac.get(url)
        if 'id' in resp:
            return resp['id']
        else:
            return ''

    def fetch_img(self, url, use_cache):
        img_url = url + "?token=" + os.environ["AMIGOCLOUD_API_KEY"]
        if use_cache:
            img = self.cm.get(img_url)
        else:
            img = None
        if not img or not use_cache:
            img = urllib.request.urlopen(img_url).read()
            self.cm.put_buffer(img_url, img)
        return img

    def fetch_mixpanel_token(self):
        tracking_url = self.base_url + '/api/v1/utils/tracking/'
        resp = self.ac.get(tracking_url)
        if 'mixpanel_project_token' in resp:
            return resp['mixpanel_project_token']
        else:
            return ""

    def store_hash(self, key, value):
        self.cm.put_buffer(key, value)

    def get_hash(self, key):
        return self.cm.get(key)

    def send_analytics_event(self, category, action, label):
        if not self.mixpanel_token:
            return
        email = self.ac.get_user_email().lower()
        if email and "@" in email:
            e = {
                "event": action,
                "properties": {
                    "distinct_id": email,
                    "token": self.mixpanel_token,
                    "category": category,
                    "action": action,
                    "label": label,
                    "email": email,
                    "$email": email,
                    "user_id": str(self.ac.get_user_id()),
                    "plugin-version": self.plugin_version,
                    "server": self.base_url
                }
            }
            ejson = json.dumps(e)
            e64 = base64.b64encode(bytes(ejson, 'utf-8'))
            url = 'http://api.mixpanel.com/track/?data=' + str(e64)
            try:
                requests.get(url)
            except Exception:
                print(Exception)
            requests.get(url)


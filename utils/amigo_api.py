import base64
import json
import os

import requests

from .amigocloud import AmigoCloud


class AmigoAPI:
    def __init__(self):
        try:
            self.token = os.environ['AMIGOCLOUD_API_KEY']
        except:
            self.token = ''
        self.url = 'https://www.amigocloud.com'
        self.ac = AmigoCloud(token=self.token, base_url=self.url)
        self.mixpanel_token = self.fetch_mixpanel_token()
        self.plugin_version = "0.7"

    def set_token(self, token):
        self.token = token
        self.ac = AmigoCloud(token=self.token, base_url=self.url)
        self.mixpanel_token = self.fetch_mixpanel_token()

    def fetch_project_list(self):
        resp = self.ac.get(self.url + '/api/v1/me/projects?summary')
        if 'results' in resp:
            return resp['results']
        else:
            return []

    def fetch_dataset_list(self, project_id):
        dataset_url = self.url + '/api/v1/users/0/projects/' + project_id + '/datasets?summary'
        resp = self.ac.get(dataset_url)
        if 'results' in resp:
            return resp['results']
        else:
            return []

    def fetch_dataset_relations(self, project_id, dataset_id):  # Queries the relationships of a dataset
        relations_url = self.url + '/api/v1/users/0/projects/' + project_id + '/datasets/' + dataset_id + '/relationships/'
        resp = self.ac.get(relations_url)
        if 'results' in resp:
            return resp['results']
        else:
            return []

    def fetch_dataset_schema(self, project_id, dataset_id):
        relations_url = self.url + '/api/v1/users/0/projects/' + project_id + '/datasets/' + dataset_id + '/schema/'
        resp = self.ac.get(relations_url)
        if 'schema' in resp:
            return resp['schema']
        else:
            return []

    def fetch_mixpanel_token(self):
        tracking_url = self.url + '/api/v1/utils/tracking/'
        resp = self.ac.get(tracking_url)
        if 'mixpanel_project_token' in resp:
            return resp['mixpanel_project_token']
        else:
            return ""

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
                    "server": self.url
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


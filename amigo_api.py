import os
from amigocloud import AmigoCloud

class AmigoAPI:
    def __init__(self):
        try:
            self.token = os.environ['AMIGOCLOUD_API_KEY']
        except:
            self.token = ''
        self.url = 'https://www.amigocloud.com'
        self.ac = AmigoCloud(token=self.token, base_url=self.url)

    def set_token(self, token):
        self.token = token
        self.ac = AmigoCloud(token=self.token, base_url=self.url)

    def fetch_project_list(self):
        resp = self.ac.get(self.url + '/api/v1/me/projects?summary')
        if 'results' in resp:
            return resp['results']
        else:
            return []

    def fetch_dataset_list(self, project_id):
        dataset_url = self.url + '/api/v1/users/0/projects/' + project_id + '/datasets'
        resp = self.ac.get(dataset_url)
        return resp['results']

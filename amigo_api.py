import os
from amigocloud import AmigoCloud

class AmigoAPI:
    def __init__(self):
        token = os.environ['AMIGOCLOUD_API_KEY']
        self.ac = AmigoCloud(token=token)

    def fetch_project_list(self):
        resp = self.ac.get('https://www.amigocloud.com/api/v1/me/projects?summary')
        return resp['results']

    def fetch_dataset_list(self, project_id):
        url = 'https://www.amigocloud.com/api/v1/users/0/projects/'+ project_id +'/datasets'
        resp = self.ac.get(url)
        return resp['results']

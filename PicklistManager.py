from .amigo_api import AmigoAPI
from .QGISManager import QGISManager

class PicklistManager():
    def __init__(self):
        self.api = AmigoAPI()
        self.qgm = QGISManager()

    def managePicklists(self,ds_name, project_id,dataset_id):
        schema = self.api.fetch_dataset_schema(project_id,dataset_id)
        raw_choices = None
        field_name = None
        for field in schema:
            if 'choices' in field:
                if field['visible']:
                    raw_choices = field['choices']
                    field_name = field['name']
                    choices = self.qgm.formatChoices(raw_choices)
                    self.qgm.addValueMap(ds_name,field_name,choices)
        if raw_choices == None:
            print('No choices found or picklist marked as not visible')
            return
from .amigo_api import AmigoAPI
from .QGISManager import QGISManager


class PicklistManager:
    def __init__(self):
        self.api = AmigoAPI()
        self.qgm = QGISManager()

    def manage_picklists(self, ds_name, project_id, dataset_id):
        schema = self.api.fetch_dataset_schema(project_id, dataset_id)
        raw_choices = None
        for field in schema:
            if 'choices' in field:
                if field['visible']:
                    raw_choices = field['choices']
                    field_name = field['name']
                    choices = self.qgm.format_choices(raw_choices)
                    self.qgm.add_value_map(ds_name, field_name, choices)
        if raw_choices is None:
            print('No choices found or picklist marked as not visible')
            return

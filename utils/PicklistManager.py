from .amigo_api import AmigoAPI
from .QGISManager import QGISManager


class PicklistManager:
    def __init__(self):
        self.api = AmigoAPI()
        self.qgm = QGISManager()

    def format_choices(self, dictionary):
        r = {}
        for elem in dictionary:
            r[elem['value']] = elem['code']
        return r

    def manage_picklists(self, ds_name, ds_schema):
        raw_choices = None

        r = []

        for field in ds_schema:
            if 'choices' in field:
                if field['visible']:
                    raw_choices = field['choices']
                    field_name = field['name']
                    choices = self.format_choices(raw_choices)
                    try:
                        self.qgm.add_value_map(ds_name, field_name, choices)
                        r.append((ds_name, field_name, choices))
                    except Exception:
                        print("Couldn't access the method 'add_value_map' from utils/QGISManager")
        if raw_choices is None:
            print('No choices found or picklist marked as not visible')

        return r

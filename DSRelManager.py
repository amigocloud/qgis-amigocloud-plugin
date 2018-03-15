from .QGISManager import QGISManager


class DSRelManager:
    def __init__(self):
        self.qgm = QGISManager()

    def relate(self, relations):
        if relations:  # If relations it's not empty
            for r in relations:
                child_name = r['foreign_dataset_name']
                parent_name = r['primary_dataset_name']

                primary_key = r['primary_key']
                foreign_key = r['foreign_key']

                relation_id = str(r['id'])

                try:
                    child_layers = self.qgm.get_layer_by_name(child_name)
                    parent_layers = self.qgm.get_layer_by_name(parent_name)
                except:
                    child_layers = []
                    parent_layers = []

                if child_layers and parent_layers:  # If both layers exist
                    for child_layer, parent_layer in zip(child_layers, parent_layers):
                        self.qgm.make_relation(child_layer, parent_layer, foreign_key, primary_key, relation_id)

                else:
                    print('At least two layers are required to make a relationship. Please add another one.')



from qgis._core import QgsEditorWidgetSetup
from qgis._core import QgsProject
from qgis._core import QgsRelation
from qgis._core import QgsVectorLayer


class QGISManager:
    def __init__(self):
        # self.api = AmigoAPI()
        self.is_dev = False

    def dev_print(self, content):
        if self.is_dev:
            print(content)

    def add_layer(self, uri, name):
        v_layer = QgsVectorLayer(uri, name, "ogr")
        QgsProject.instance().addMapLayer(v_layer)

    def get_layer_by_name(self, name):
        return QgsProject.instance().mapLayersByName('b\'' + name + '\'')

    def make_relation(self, child_layer, parent_layer, foreign_key, primary_key, relation_id):
        relation_name = 'from_' + parent_layer.name() + '_to_' + child_layer.name()
        # Setting up the relation
        rel = QgsRelation()
        rel.setReferencingLayer(parent_layer.id())
        rel.setReferencedLayer(child_layer.id())
        rel.addFieldPair(primary_key, foreign_key)
        rel.setId(relation_id)
        rel.setName(relation_name)

        # Adding the relation only if it's valid
        if rel.isValid():
            QgsProject.instance().relationManager().addRelation(rel)
            self.dev_print('Relation added: ' + relation_name)
        else:
            self.dev_print('Relation failed </3')

    def add_value_map(self, layer_name, field_name, dict_choices):
        try:
            layers = QgsProject.instance().mapLayersByName(layer_name)
            if layers and dict_choices:
                for layer in layers:
                    field_index = layer.fields().indexFromName(field_name)
                    editor_widget_setup = QgsEditorWidgetSetup('ValueMap', {
                        'map': dict_choices
                    }
                                                               )
                    layer.setEditorWidgetSetup(field_index, editor_widget_setup)
                    self.dev_print('ValueMap added')
            else:
                self.dev_print("Layer or choices don't exist")
                return
        except Exception:
            print('Exception raised')
            return

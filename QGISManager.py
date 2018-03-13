from qgis._core import QgsEditorWidgetSetup
from qgis._core import QgsProject
from qgis._core import QgsRelation
from qgis._core import QgsVectorLayer
from .amigo_api import AmigoAPI

api = AmigoAPI()

class QGISManager():
    def addLayer(self,uri,name):
        vlayer = QgsVectorLayer(uri, name, "ogr")
        QgsProject.instance().addMapLayer(vlayer)

    def getLayerByName(self, name):
        return QgsProject.instance().mapLayersByName('b\'' + name + '\'')

    def makeRelation(self,child_layer, parent_layer, foreign_key, primary_key, relation_id):
        relation_name = 'from_' + child_layer.name() + '_to_' + parent_layer.name()
        # Setting up the relation
        rel = QgsRelation()
        rel.setReferencingLayer(child_layer.id())
        rel.setReferencedLayer(parent_layer.id())
        rel.addFieldPair(foreign_key, primary_key)
        rel.setId(relation_id)
        rel.setName(relation_name)

        # Adding the relation only if it's valid
        if rel.isValid():
            QgsProject.instance().relationManager().addRelation(rel)
            print('Relation added: ' + relation_name)
        else:
            print('Relation failed </3')


    def formatChoices(self, dict):
        r = {}
        for elem in dict:
            r[elem['value']] = elem['code']
        return r

    def addValueMap(self, layer_name, field_name, dict_choices):
        try:
            layers = QgsProject.instance().mapLayersByName(layer_name)
            if layers and dict_choices:
                for layer in layers:
                    fieldIndex = layer.fields().indexFromName(field_name)
                    editor_widget_setup = QgsEditorWidgetSetup('ValueMap', {
                        'map': dict_choices
                    }
                                                               )
                    layer.setEditorWidgetSetup(fieldIndex, editor_widget_setup)
                    print('ValueMap added')
            else:
                print('Layer or choices doesn\'t exist')
                return
        except Exception:
            print('Exception raised')
            return
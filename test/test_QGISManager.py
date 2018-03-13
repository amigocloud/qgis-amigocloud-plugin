from qgis._core import QgsProject

from QGISManager import QGISManager

qgm = QGISManager()

def test_makeRelation():
    qgm.addLayer('','child_layer')
    qgm.addLayer('','parent_layer')

    test_child_layer = qgm.getLayerByName('child_layer')
    test_parent_layer = qgm.getLayerByName('parent_layer')
    test_foreign_key = 'fkey'
    test_primary_key = 'pkey'
    test_rel_id = 'id123'

    qgm.makeRelation(test_child_layer,test_parent_layer,test_foreign_key,test_primary_key,test_rel_id)
    print('Test relation made!')
    # QgsProject.instance().removeMapLayers([test_child_layer.id(),test_parent_layer.id()])
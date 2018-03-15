from qgis._core import QgsProject

from QGISManager import QGISManager

qgm = QGISManager()

def test_makeRelation():
    qgm.add_layer('', 'child_layer')
    qgm.add_layer('', 'parent_layer')

    test_child_layer = qgm.get_layer_by_name('child_layer')
    test_parent_layer = qgm.get_layer_by_name('parent_layer')
    test_foreign_key = 'fkey'
    test_primary_key = 'pkey'
    test_rel_id = 'id123'

    qgm.make_relation(test_child_layer, test_parent_layer, test_foreign_key, test_primary_key, test_rel_id)
    print('Test relation made!')
    # QgsProject.instance().removeMapLayers([test_child_layer.id(),test_parent_layer.id()])
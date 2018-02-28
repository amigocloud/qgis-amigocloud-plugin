from qgis._core import QgsProject
from qgis._core import QgsRelation

class DSRelManager():

    def getRelations(self):
        relations = self.api.fetch_dataset_relations(self.dlg.get_project_id(),self.dlg.get_dataset_id())
        return relations

    def manageRelations(self,relations):
        if relations: # If relations it's not empty
            for r in relations:
                child_name = r['foreign_dataset_name']
                parent_name = r['primary_dataset_name']

                primary_key = r['primary_key']
                foreign_key = r['foreign_key']

                relation_id = str(r['id'])

                # Formatting required for QGIS layers' names
                child_layer = QgsProject.instance().mapLayersByName('b\'' + child_name + '\'')
                parent_layer = QgsProject.instance().mapLayersByName('b\'' + parent_name + '\'')

                if child_layer and parent_layer:  # If both layers exist
                    child_layer = child_layer[0]
                    parent_layer = parent_layer[0]

                    relation_name = 'from_' + child_layer.name() + '_to_' + parent_layer.name()

                    print('Relation name: ' + relation_name)
                    print('\tChild id: ' + child_layer.id())
                    print('\tParent id: ' + parent_layer.id())

                    # Setting up the relation
                    rel = QgsRelation()
                    rel.setReferencingLayer(child_layer.id())
                    rel.setReferencedLayer(parent_layer.id())
                    rel.addFieldPair(foreign_key, primary_key)
                    rel.setId(relation_id)
                    rel.setName(relation_name)

                    print('\tIs it valid? ' + str(rel.isValid()))

                    # Adding the relation only if it's valid
                    if rel.isValid():
                        QgsProject.instance().relationManager().addRelation(rel)
                        print('Relation added: ' + relation_name)
                    else:
                        print('Relation failed </3')
                else:
                    print('At least two layers are required to make a relationship. Please add another one.')
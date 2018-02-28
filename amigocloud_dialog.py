# -*- coding: utf-8 -*-
"""
/***************************************************************************
 amigocloudDialog
                                 A QGIS plugin
 amigocloud
                             -------------------
        begin                : 2015-09-25
        git sha              : $Format:%H$
        copyright            : (C) 2015 by AmigoCloud
        email                : victor@amigocloud.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import urllib
import urllib.request

from PyQt5 import QtGui, uic
from PyQt5.QtCore import QSettings, Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QDialog, QListWidget, QLineEdit, QListWidgetItem, QPushButton
from .CacheManager import CacheManager
from .amigo_api import AmigoAPI

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'amigocloud_dialog_base.ui'))

cm = CacheManager()
cm.initializeDB()

class amigocloudDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(amigocloudDialog, self).__init__(parent)

        self.amigo_api = AmigoAPI()
        self.projects_list = self.amigo_api.fetch_project_list()
        self.iconSize = QSize(50, 50)
        self.settings = QSettings('AmigoCloud', 'QGIS.Plugin')
        self.setupUi(self)
        self.p_list_widget = self.findChild(QListWidget, 'projects_listWidget')
        self.p_list_widget.itemClicked.connect(self.project_clicked)

        self.ds_list_widget = self.findChild(QListWidget, 'datasets_listWidget')
        self.ds_list_widget.itemClicked.connect(self.dataset_clicked)

        self.syncButton = QPushButton('Sync.',self)
        self.syncButton.move(698,32)
        self.syncButton.clicked.connect(self.sync)



        self.apiKeyValue = self.settings.value('apiKeyValue')

        self.readAllFromLocal = []


        self.token_lineEdit = self.findChild(QLineEdit, 'token_lineEdit')
        self.token_lineEdit.textChanged.connect(self.on_token_changed)
        if self.get_token() and len(self.get_token()) > 0:
            self.token_lineEdit.setText(self.get_token())

        self.p_list_widget = self.findChild(QListWidget, 'projects_listWidget')

        self.setFixedSize(800, 460)

        self.amigo_api.send_analytics_event("User",
                                            "Start (QGIS-plugin)",
                                            self.amigo_api.ac.get_user_email())


    def sync(self):
        cm.devPrint("Synchronizing...")
        self.projects_list = self.amigo_api.fetch_project_list()
        if len(self.projects_list) > 0:
            os.environ['AMIGOCLOUD_API_KEY'] = self.get_token()
            self.fill_project_list()

    def get_name(self):
        return self.settings.value('nameValue')

    def get_project_id(self):
        return self.settings.value('projectIdValue')

    def get_dataset_id(self):
        return self.settings.value('datasetIdValue')

    def get_token(self):
        return self.settings.value('tokenValue')


    def load_image(self, url):
        url = url + '?token=' + os.environ['AMIGOCLOUD_API_KEY']
        data = urllib.request.urlopen(url).read()
        image = QtGui.QImage()
        image.loadFromData(data)
        return image

    # Makes a new QIcon based on a local image
    def newIcon(self, pixmapContent):
        # Pixmap object that will contain the image
        pixmap = QPixmap()
        # Now the pixmap contains the information from the image
        pixmap.loadFromData(pixmapContent)
        # A new icon is created with the pixmap as its background image
        icon = QIcon(pixmap)
        return icon

    def on_token_changed(self, token):
        self.settings.setValue('tokenValue', token)
        self.amigo_api.set_token(token)
        self.projects_list = self.amigo_api.fetch_project_list()
        if len(self.projects_list) > 0:
            os.environ['AMIGOCLOUD_API_KEY'] = self.get_token()
            self.fill_project_list()

    def project_clicked(self, item):
        self.fill_datasets_list(str(item.data(Qt.UserRole)))
        self.settings.setValue('projectIdValue', str(item.data(Qt.UserRole)))

    def dataset_clicked(self, item):
        self.settings.setValue('datasetIdValue', str(item.data(Qt.UserRole)))
        self.settings.setValue('nameValue', str(item.text().encode('utf-8')))

    def fill_project_list(self):
        self.p_list_widget.clear()
        remoteUrls = []
        for p_iterator, project in enumerate(self.projects_list):
            p_url = project['url']
            p_hash = project['hash']

            remoteUrls.append(p_url)

            # Checks if there is a new project on the remote server
            if cm.verifyProjectExists(p_url):
                # Check if the project's hash has changed. If not, just load everything from local
                if cm.verifyProjectHashChanged(p_hash):
                    cm.setProjectUpdated(p_url, 0)
                    p_name = project['name']
                    p_img_hash = project['preview_image_hash']
                    if(cm.verifyProjectImageHashChanged(p_img_hash)):
                        p_img_url = project['preview_image']
                        cm.updateProjectAll(p_url, p_hash, p_name, p_img_url, p_img_hash)
                        cm.devPrint("Updating all from project [" + p_name + "]")
                    else:
                        cm.updateProjectName(p_url, p_hash, p_name)
                        cm.devPrint("Renaming project to: [" + p_name + "]")
                else:
                    # Read all from this project from local
                    cm.setProjectUpdated(p_url, 1)
                    cm.devPrint("Project is updated")
            else:
                p_id = project['id']
                p_name = project['name']
                p_img_url = project['preview_image']
                p_img_hash = project['preview_image_hash']
                p_updated = 0

                cm.insertNewProject(p_url, p_id, p_name, p_hash, p_img_url, p_img_hash, p_updated)
                cm.devPrint("New project found: [" + p_name + "]. Inserting to local DB...")

            projectFromLocal = cm.loadFromProjects(p_url)
            # "fl" = from local
            fl_p_id = projectFromLocal[1]
            fl_p_name = projectFromLocal[2]
            fl_p_img = projectFromLocal[4]

            cm.devPrint("Reading project [" + fl_p_name + "] from local..." + "\n")

            # Individual item of the project list. Contains the actual name of the project.
            item = QListWidgetItem(fl_p_name, self.p_list_widget)
            # Now the item has also an icon with the project's preview image
            item.setIcon(self.newIcon(fl_p_img))
            item.setData(Qt.UserRole, fl_p_id)
            # Adds the item to the list
            self.p_list_widget.addItem(item)
            # Resizes the icon so it can be properly visualized
            self.p_list_widget.setIconSize(self.iconSize)

        localUrls = cm.loadAllUrlsFromProjectsLocal()
        cm.projectTrashcan(remoteUrls, localUrls)
        return self.p_list_widget

    def fill_datasets_list(self, project_id):
        self.ds_list_widget.clear()
        dataset_list = self.amigo_api.fetch_dataset_list(project_id)
        ds_p_url_toUpdate = None
        remoteUrls = []
        for dataset in dataset_list:
            if dataset['visible']:
                ds_url = dataset['url']
                ds_hash = dataset['hash']
                ds_p_url = dataset['project']

                ds_p_url_toUpdate = ds_p_url
                remoteUrls.append(ds_url)
                # Check if there's a new dataset on remote
                if cm.verifyDatasetExists(ds_url):
                    if cm.checkProjectUpdated(ds_p_url) == 0:   # If the project is not updated, download accordingly
                        if cm.verifyDatasetHashChanged(ds_hash): # If the hash has changed...
                            ds_name = dataset['name']
                            ds_img_hash = dataset['preview_image_hash']
                            if cm.verifyDatasetImageHashChanged(ds_img_hash):
                                ds_img_url = dataset['preview_image']
                                cm.updateDatasetAll(ds_url, ds_hash, ds_name, ds_img_url, ds_img_hash)
                                cm.devPrint("Updating all from dataset [" + ds_name + "]")
                            else:
                                cm.updateProjectName(ds_url, ds_hash, ds_name)
                                cm.devPrint("Renaming dataset to: [" + ds_name + "]")
                    else:
                        cm.devPrint("The project is up to date. Loading all from local")
                else:
                    ds_id = dataset['id']
                    ds_name = dataset['name']
                    ds_img_url = dataset['preview_image']
                    ds_img_hash = dataset['preview_image_hash']

                    cm.insertNewDataset(ds_p_url, ds_url, ds_id, ds_name, ds_hash, ds_img_url, ds_img_hash)
                    cm.devPrint("New dataset found: [" + ds_name + "]. Inserting to local DB...")

                datasetFromLocal = cm.loadFromDatasets(ds_url)

                # "fl" = from local
                fl_ds_id = datasetFromLocal[2]
                fl_ds_name = datasetFromLocal[3]
                fl_ds_img = datasetFromLocal[5]

                item = QListWidgetItem(fl_ds_name, self.ds_list_widget)
                item.setIcon(self.newIcon(fl_ds_img))
                item.setData(Qt.UserRole, fl_ds_id)
                self.ds_list_widget.addItem(item)
                self.ds_list_widget.setIconSize(self.iconSize)

        localUrls = cm.loadAllUrlsFromDatasetsLocal(ds_p_url_toUpdate)
        cm.datasetTrashcan(remoteUrls, localUrls) # Deletes the datasets on the cache that are no longer on remote
        cm.setProjectUpdated(ds_p_url_toUpdate, 1)  # Sets the parent project as updated
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
from PyQt5.QtWidgets import QDialog, QListWidget, QLineEdit, QListWidgetItem

from .amigo_api import AmigoAPI

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'amigocloud_dialog_base.ui'))


class amigocloudDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(amigocloudDialog, self).__init__(parent)

        self.amigo_api = AmigoAPI()
        self.projects_list = self.amigo_api.fetch_project_list()
        self.iconSize = QSize(50,50)
        self.settings = QSettings('AmigoCloud', 'QGIS.Plugin')
        self.setupUi(self)
        self.p_list_widget = self.findChild(QListWidget, 'projects_listWidget')
        self.p_list_widget.itemClicked.connect(self.project_clicked)

        self.ds_list_widget = self.findChild(QListWidget, 'datasets_listWidget')
        self.ds_list_widget.itemClicked.connect(self.dataset_clicked)

        self.apiKeyValue = self.settings.value('apiKeyValue')

        self.token_lineEdit = self.findChild(QLineEdit, 'token_lineEdit')
        self.token_lineEdit.textChanged.connect(self.on_token_changed)
        if self.get_token() and len(self.get_token()) > 0:
            self.token_lineEdit.setText(self.get_token())

        self.p_list_widget = self.findChild(QListWidget, 'projects_listWidget')
        self.p_list_widget.itemClicked.connect(self.project_clicked)

        self.fill_project_list()
        self.setFixedSize(800, 460)

        self.amigo_api.send_analytics_event("User",
                                        "Start (QGIS-plugin)",
                                        self.amigo_api.ac.get_user_email())

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

    # Makes a new QIcon based on a url that provides the image for the icon
    def newIcon(self, url):
        # Url that contains background image.
        # It's completed with the necessary key to access the remote server
        url = url + '?token=' + os.environ['AMIGOCLOUD_API_KEY']
        # Reading of the url
        data = urllib.request.urlopen(url).read()
        # Pixmap object that will contain the image
        pixmap = QPixmap()
        # Now the pixmap contains the information from the url
        pixmap.loadFromData(data)
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

    def dataset_clicked(self, item):
        self.settings.setValue('datasetIdValue', str(item.data(Qt.UserRole)))
        self.settings.setValue('nameValue', str(item.text().encode('utf-8')))

    def fill_datasets_list(self, project_id):
        self.ds_list_widget.clear()
        dataset_list = self.amigo_api.fetch_dataset_list(project_id)
        for dataset in dataset_list:
            if dataset['visible']:
                url = dataset['preview_image']
                item = QListWidgetItem(dataset['name'], self.ds_list_widget)
                item.setIcon(self.newIcon(url))
                item.setData(Qt.UserRole, dataset['id'])
                self.ds_list_widget.addItem(item)
                self.ds_list_widget.setIconSize(self.iconSize)

    def project_clicked(self, item):
        self.fill_datasets_list(str(item.data(Qt.UserRole)))
        self.settings.setValue('projectIdValue', str(item.data(Qt.UserRole)))


    def fill_project_list(self):
        self.p_list_widget.clear()
        for project in self.projects_list:
            #The url with information of the preview image of the actual project
            url = project['preview_image']
            #Individual item of the project list. Contains the actual name of the project.
            item = QListWidgetItem(project['name'], self.p_list_widget)
            #Now the item has also an icon with the project's preview image
            item.setIcon(self.newIcon(url))
            item.setData(Qt.UserRole, project['id'])
            #Adds the item to the list
            self.p_list_widget.addItem(item)
            #Resizes the icon so it can be properly visualized
            self.p_list_widget.setIconSize(self.iconSize)
        return self.p_list_widget


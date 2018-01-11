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

from PyQt5 import QtGui, uic
from PyQt5.QtCore import QSettings, Qt
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
                item = QListWidgetItem(dataset['name'], self.ds_list_widget)
                item.setData(Qt.UserRole, dataset['id'])
                self.ds_list_widget.addItem(item)

    def project_clicked(self, item):
        self.fill_datasets_list(str(item.data(Qt.UserRole)))
        self.settings.setValue('projectIdValue', str(item.data(Qt.UserRole)))

    def fill_project_list(self):
        self.p_list_widget.clear()
        for project in self.projects_list:
            item = QListWidgetItem(project['name'], self.p_list_widget)
            item.setData(Qt.UserRole, project['id'])
            self.p_list_widget.addItem(item)
        return self.p_list_widget


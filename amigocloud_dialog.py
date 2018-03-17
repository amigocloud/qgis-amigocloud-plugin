# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AmigoCloudDialog
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
import re
import urllib
import urllib.request
import json

from PyQt5 import QtGui, uic
from PyQt5.QtCore import QSettings, Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QDialog, QListWidget, QLineEdit, QListWidgetItem, QPushButton

from .utils.CacheManager import CacheManager
from .utils.amigo_api import AmigoAPI

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'amigocloud_dialog_base.ui'))


class AmigoCloudDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(AmigoCloudDialog, self).__init__(parent)

        self.amigo_api = AmigoAPI()
        self.cm = CacheManager()
        self.cm.init_db()
        self.projects_list = self.amigo_api.fetch_project_list()
        self.iconSize = QSize(50, 50)
        self.settings = QSettings('AmigoCloud', 'QGIS.Plugin')
        self.setupUi(self)
        self.p_list_widget = self.findChild(QListWidget, 'projects_listWidget')
        self.p_list_widget.itemClicked.connect(self.project_clicked)

        self.ds_list_widget = self.findChild(QListWidget, 'datasets_listWidget')
        self.ds_list_widget.itemClicked.connect(self.dataset_clicked)

        self.syncButton = QPushButton('Sync.', self)
        self.syncButton.move(698, 32)
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
        self.cm.dev_print("Synchronizing...")
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
    def new_icon(self, pixmap_content):
        # Pixmap object that will contain the image
        pixmap = QPixmap()
        # Now the pixmap contains the information from the image
        pixmap.loadFromData(pixmap_content)
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
        for project in self.projects_list:
            p_url = project["url"]
            p_id = project["id"]
            p_name = project["name"]
            p_img_hash = project["preview_image_hash"]
            p_img_url = project["preview_image"]

            if self.cm.verify_row_exists(p_url):
                if self.cm.verify_img_hash_changed(p_img_hash, True):
                    self.cm.update_img(p_img_hash, p_img_url, p_url)
            else:
                self.cm.add_row(p_url, p_name, None, None, p_img_hash, p_img_url)

            p_img = self.cm.fetch_img(p_url)

            # Individual item of the project list. Contains the actual name of the project.
            item = QListWidgetItem(p_name, self.p_list_widget)
            # Now the item has also an icon with the project's preview image
            item.setIcon(self.new_icon(p_img))
            item.setData(Qt.UserRole, p_id)
            # Adds the item to the list
            self.p_list_widget.addItem(item)
            # Resizes the icon so it can be properly visualized
            self.p_list_widget.setIconSize(self.iconSize)

        return self.p_list_widget

    def fill_datasets_list(self, project_id):
        self.ds_list_widget.clear()
        dataset_list = self.amigo_api.fetch_dataset_list(project_id)
        for dataset in dataset_list:
            if dataset["visible"]:
                ds_url = dataset["url"]
                ds_id = dataset["id"]
                ds_name = dataset["name"]
                ds_schema_hash = dataset["schema_hash"]
                ds_img_hash = dataset["preview_image_hash"]
                ds_img_url = dataset["preview_image"]

                if self.cm.verify_row_exists(ds_url):
                    # TODO: Change the second parameter to True when issue #3708 of amigoserver is solved
                    if self.cm.verify_img_hash_changed(ds_img_hash, False):
                        self.cm.update_img(ds_img_hash, ds_img_url, ds_url)
                    # TODO: Change the second parameter to True when issue #3735 of amigoserver is solved
                    if self.cm.verify_schema_hash_changed(ds_schema_hash, False):
                        ds_schema = self.amigo_api.fetch_dataset_schema_from_url(ds_url)
                        ds_schema = self.cm.format_json_to_insert(ds_schema)
                        self.cm.update_schema(ds_schema_hash, ds_schema, ds_url)
                else:
                    ds_schema = self.amigo_api.fetch_dataset_schema_from_url(ds_url)
                    ds_schema = self.cm.format_json_to_insert(ds_schema)
                    self.cm.add_row(ds_url, ds_name, ds_schema_hash, ds_schema, ds_img_hash, ds_img_url)

                ds_img = self.cm.fetch_img(ds_url)
                item = QListWidgetItem(ds_name, self.ds_list_widget)
                item.setIcon(self.new_icon(ds_img))
                item.setData(Qt.UserRole, ds_id)
                self.ds_list_widget.addItem(item)
                self.ds_list_widget.setIconSize(self.iconSize)


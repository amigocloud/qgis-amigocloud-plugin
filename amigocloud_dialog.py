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
import urllib
import urllib.request

from PyQt5 import QtGui, uic
from PyQt5.QtCore import QSettings, Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QDialog, QListWidget, QLineEdit, QListWidgetItem, QPushButton, QLabel, QToolButton

from .settings_dialog import SettingsDialog
from .utils.amigo_api import AmigoAPI

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'amigocloud_dialog_base.ui'))


class AmigoCloudDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(AmigoCloudDialog, self).__init__(parent)

        self.settings = QSettings('AmigoCloud', 'QGIS.Plugin')
        self.amigo_api = AmigoAPI(self.settings)
        self.projects_list = self.amigo_api.fetch_project_list(False)
        self.iconSize = QSize(50, 50)
        self.setupUi(self)
        self.p_list_widget = self.findChild(QListWidget, 'projects_listWidget')
        self.p_list_widget.itemClicked.connect(self.project_clicked)

        self.ds_list_widget = self.findChild(QListWidget, 'datasets_listWidget')
        self.ds_list_widget.itemClicked.connect(self.dataset_clicked)

        self.apiKeyValue = self.settings.value('apiKeyValue')

        self.user_label = self.findChild(QLabel, 'user_label')
        self.user_label.setText('User: ' + self.amigo_api.get_user_name())

        self.p_list_widget = self.findChild(QListWidget, 'projects_listWidget')

        self.setFixedSize(800, 460)

        self.amigo_api.send_analytics_event("User",
                                            "Start (QGIS-plugin)",
                                            self.amigo_api.ac.get_user_email())

        self.settings_button = self.findChild(QToolButton, 'settings_button')
        self.settings_button.clicked.connect(self.settings_pressed)

        self.fetch_project_list()

    def settings_pressed(self):
        dialog = SettingsDialog()
        dialog.show()
        dialog.exec_()
        self.fetch_project_list()

    def get_token(self):
        return self.amigo_api.get_token()

    def get_name(self):
        return self.settings.value('nameValue')

    def get_project_id(self):
        return self.settings.value('projectIdValue')

    def get_dataset_id(self):
        return self.settings.value('datasetIdValue')

    def load_image(self, url):
        url = url + '?token=' + self.amigo_api.get_token()
        data = urllib.request.urlopen(url).read()
        image = QtGui.QImage()
        image.loadFromData(data)
        return image

    def new_icon(self, pixmap_content):
        pixmap = QPixmap()
        pixmap.loadFromData(pixmap_content)
        icon = QIcon(pixmap)
        return icon

    def fetch_project_list(self):
        self.projects_list = self.amigo_api.fetch_project_list(False)
        self.fill_project_list()

    def project_clicked(self, item):
        self.fill_datasets_list(str(item.data(Qt.UserRole)))
        self.settings.setValue('projectIdValue', str(item.data(Qt.UserRole)))

    def dataset_clicked(self, item):
        self.settings.setValue('datasetIdValue', str(item.data(Qt.UserRole)))
        self.settings.setValue('nameValue', str(item.text()))

    def fill_project_list(self):
        self.p_list_widget.clear()
        self.ds_list_widget.clear()
        for project in self.projects_list:
            p_url = project["url"]
            p_id = project["id"]
            p_name = project["name"]
            p_img_hash = project["preview_image_hash"]
            p_img_url = project["preview_image"]

            # Check the hash to see if preview image has changed
            hash_key = p_url
            stored_hash = self.amigo_api.get_hash(hash_key)
            use_cache = False
            if p_img_hash == stored_hash:
                use_cache = True

            p_img = self.amigo_api.fetch_img(p_img_url, use_cache=use_cache)
            self.amigo_api.store_hash(hash_key, p_img_hash)

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

                # Check the hash to see if preview image has changed
                hash_key = ds_url
                stored_hash = self.amigo_api.get_hash(hash_key)
                use_cache = False
                if ds_img_hash == stored_hash:
                    use_cache = True

                ds_img = self.amigo_api.fetch_img(ds_img_url, use_cache=use_cache)
                self.amigo_api.store_hash(hash_key, ds_img_hash)

                item = QListWidgetItem(ds_name, self.ds_list_widget)
                item.setIcon(self.new_icon(ds_img))
                item.setData(Qt.UserRole, ds_id)
                self.ds_list_widget.addItem(item)
                self.ds_list_widget.setIconSize(self.iconSize)


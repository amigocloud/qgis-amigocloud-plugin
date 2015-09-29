# -*- coding: utf-8 -*-
"""
/***************************************************************************
 amigocloudDialog
                                 A QGIS plugin
 amigocloud
                             -------------------
        begin                : 2015-09-25
        git sha              : $Format:%H$
        copyright            : (C) 2015 by amigocloud
        email                : geodrinx@gmail.com
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

from PyQt4 import QtGui, uic
from PyQt4.QtCore import QSettings

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'amigocloud_dialog_base.ui'))


class amigocloudDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(amigocloudDialog, self).__init__(parent)

        self.settings = QSettings('AmigoCloud', 'QGIS.Plugin')

        self.nameValue = self.settings.value('nameValue')
        self.projectIdValue = self.settings.value('projectIdValue')
        self.datasetIdValue = self.settings.value('datasetIdValue')
        self.apiKeyValue = self.settings.value('apiKeyValue')

        layerName = QtGui.QLabel('Layer Name')

        projectId = QtGui.QLabel("<a href=\"https://www.amigocloud.com/dashboard/index.html#/user-dashboard\"> <font face=verdana>Project ID</font> </a>")
        projectId.setOpenExternalLinks(True)

        datasetId = QtGui.QLabel("<a href=\"https://www.amigocloud.com/dashboard/index.html#/user-dashboard\"> <font face=verdana>Dataset ID</font> </a>")
        datasetId.setOpenExternalLinks(True)

        apiKey = QtGui.QLabel("<a href=\"https://www.amigocloud.com/accounts/tokens\"> <font face=verdana>AmigoCloud API Token</font> </a>")
        apiKey.setOpenExternalLinks(True)

        self.layerNameEdit = QtGui.QLineEdit(self.nameValue)
        self.projectIdEdit = QtGui.QLineEdit(self.projectIdValue)
        self.datasetIdEdit = QtGui.QLineEdit(self.datasetIdValue)
        self.apiKeyEdit = QtGui.QLineEdit(self.apiKeyValue)

        grid = QtGui.QGridLayout()
        grid.setSpacing(-10)

        grid.addWidget(layerName, 0, 0)
        grid.addWidget(self.layerNameEdit, 0, 1)

        grid.addWidget(projectId, 1, 0)
        grid.addWidget(self.projectIdEdit, 1, 1)

        grid.addWidget(datasetId, 2, 0)
        grid.addWidget(self.datasetIdEdit, 2, 1)

        grid.addWidget(apiKey, 3, 0)
        grid.addWidget(self.apiKeyEdit, 3, 1)

        self.setLayout(grid)
        self.setFixedSize(450, 280)
        self.setupUi(self)

    def store_values(self):
        self.settings.setValue('nameValue', self.layerNameEdit.text())
        self.settings.setValue('projectIdValue', self.projectIdEdit.text())
        self.settings.setValue('datasetIdValue', self.datasetIdEdit.text())
        self.settings.setValue('apiKeyValue', self.apiKeyEdit.text())

# -*- coding: utf-8 -*-
"""
/***************************************************************************
 amigocloud
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
import os.path

from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction

from .amigocloud_dialog import AmigoCloudDialog
from .utils.DSRelManager import DSRelManager
from .utils.PicklistManager import PicklistManager
from .utils.QGISManager import QGISManager

class AmigoCloudQ:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'amigocloud_{}.qm'.format(locale))

        self.qgm = QGISManager()

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                # TODO: Fix this problem below. The function is expecting something else.
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = AmigoCloudDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&AmigoCloud')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'AmigoCloud')
        self.toolbar.setObjectName(u'AmigoCloud')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('AmigoCloud', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent = None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToWebMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/amigocloud/icon.png'

        self.add_action(
            icon_path,
            text=self.tr(u'AmigoCloud'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginWebMenu(
                self.tr(u'&AmigoCloud'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def run(self):
        """Run method that performs all the real work"""

        self.dlg.setModal(False)
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            if self.dlg.get_project_id() and self.dlg.get_dataset_id():
                self.dlg.amigo_api.send_analytics_event("User",
                                                        "Layer Added (QGIS-plugin)",
                                                        self.dlg.amigo_api.get_user_email())
                if len(self.dlg.get_token()) > 0:
                    uri = "AmigoCloud:" + self.dlg.get_project_id() + " datasets=" + self.dlg.get_dataset_id() + \
                          " AMIGOCLOUD_API_KEY=" + self.dlg.get_token()
                else:
                    uri = "AmigoCloud:" + self.dlg.get_project_id() + " datasets=" + self.dlg.get_dataset_id()
                self.qgm.add_layer(uri, self.dlg.get_name())
                rel_manager = DSRelManager()
                relations = self.dlg.amigo_api.fetch_dataset_relations(self.dlg.get_project_id(), self.dlg.get_dataset_id())
                rel_manager.relate(relations)
                pk_manager = PicklistManager()
                schema = self.dlg.amigo_api.fetch_schema(self.dlg.amigo_api.get_user_id(), self.dlg.get_project_id(), self.dlg.get_dataset_id(), False)
                if schema:
                    pk_manager.manage_picklists(self.dlg.get_name(), schema)
            else:
                self.dlg.amigo_api.send_analytics_event("User",
                                                        "Layer Add Failed (QGIS-plugin)",
                                                        self.dlg.amigo_api.get_user_email())

import os
from PyQt5 import QtGui, uic
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtWidgets import QDialog, QLineEdit
from .utils.amigo_api import AmigoAPI

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'settings_dialog.ui'))


class SettingsDialog(QDialog, FORM_CLASS):
    def __init__(self, on_token_changed_callback, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.on_token_changed_callback = on_token_changed_callback
        self.setupUi(self)
        self.settings = QSettings('AmigoCloud', 'QGIS.Plugin')
        self.amigo_api = AmigoAPI(self.settings)

        self.token_lineEdit = self.findChild(QLineEdit, 'token_lineEdit')
        self.token_lineEdit.editingFinished.connect(self.on_token_changed)
        if self.get_token() and len(self.get_token()) > 0:
            self.token_lineEdit.setText(self.get_token())

        try:
            self.api_url = os.environ['AMIGOCLOUD_API_URL']
        except:
            self.api_url = 'https://app.amigocloud.com/api/v1'

        self.url_lineEdit = self.findChild(QLineEdit, 'url_lineEdit')
        self.url_lineEdit.editingFinished.connect(self.on_url_changed)
        if self.api_url and len(self.api_url) > 0:
            self.url_lineEdit.setText(self.api_url)

    def on_token_changed(self):
        token = self.token_lineEdit.text()
        self.settings.setValue('tokenValue', token)
        if self.on_token_changed_callback is not None:
            self.on_token_changed_callback()

    def on_url_changed(self):
        url = self.url_lineEdit.text()
        os.environ['AMIGOCLOUD_API_URL'] = url
        self.settings.setValue('urlValue', url)

    def get_token(self):
        return self.settings.value('tokenValue')

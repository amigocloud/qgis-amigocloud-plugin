import os
from PyQt5 import QtGui, uic
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtWidgets import QDialog, QLineEdit
from .utils.amigo_api import AmigoAPI

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'settings_dialog.ui'))


class SettingsDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.setupUi(self)
        self.settings = QSettings('AmigoCloud', 'QGIS.Plugin')
        self.amigo_api = AmigoAPI(self.get_token())
        self.token_lineEdit = self.findChild(QLineEdit, 'token_lineEdit')
        self.token_lineEdit.editingFinished.connect(self.on_token_changed)
        if self.get_token() and len(self.get_token()) > 0:
            self.token_lineEdit.setText(self.get_token())

    def on_token_changed(self):
        token = self.token_lineEdit.text()
        self.settings.setValue('tokenValue', token)
        self.amigo_api.set_token(token)

    def get_token(self):
        return self.settings.value('tokenValue')

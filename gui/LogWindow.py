# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'LogWindow.ui'
#
# Created: Tue Mar 10 14:47:02 2009
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_LogWindow(object):
    def setupUi(self, LogWindow):
        LogWindow.setObjectName("LogWindow")
        LogWindow.resize(400, 300)
        self.verticalLayout = QtGui.QVBoxLayout(LogWindow)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtGui.QLabel(LogWindow)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.logText = QtGui.QPlainTextEdit(LogWindow)
        self.logText.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.logText.setObjectName("logText")
        self.verticalLayout.addWidget(self.logText)
        self.closeButton = QtGui.QPushButton(LogWindow)
        self.closeButton.setObjectName("closeButton")
        self.verticalLayout.addWidget(self.closeButton)

        self.retranslateUi(LogWindow)
        QtCore.QObject.connect(self.closeButton, QtCore.SIGNAL("released()"), LogWindow.close)
        QtCore.QMetaObject.connectSlotsByName(LogWindow)

    def retranslateUi(self, LogWindow):
        LogWindow.setWindowTitle(QtGui.QApplication.translate("LogWindow", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("LogWindow", "Conversion completed. Review the log to see if there were errors.", None, QtGui.QApplication.UnicodeUTF8))
        self.closeButton.setText(QtGui.QApplication.translate("LogWindow", "Close", None, QtGui.QApplication.UnicodeUTF8))


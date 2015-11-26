# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\nstevenson\AppData\Roaming\Luxology\Scripts\europa\uiModelExportEntry.ui'
#
# Created: Tue Nov 03 16:51:49 2015
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_ModelExportEntry(object):
    def setupUi(self, ModelExportEntry):
        ModelExportEntry.setObjectName("ModelExportEntry")
        ModelExportEntry.resize(678, 26)
        ModelExportEntry.setStyleSheet("QFrame { \n"
"    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgb(255, 170, 0), stop:1 rgba(255, 255, 255, 0))\n"
"}")
        self.horizontalLayout = QtGui.QHBoxLayout(ModelExportEntry)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame = QtGui.QFrame(ModelExportEntry)
        self.frame.setObjectName("frame")
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.frame)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setContentsMargins(2, 2, 2, 2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout_13 = QtGui.QHBoxLayout()
        self.horizontalLayout_13.setSpacing(5)
        self.horizontalLayout_13.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.selected_pushButton = QtGui.QPushButton(self.frame)
        self.selected_pushButton.setMaximumSize(QtCore.QSize(30, 20))
        self.selected_pushButton.setStyleSheet("QPushButton{ background-color: rgb(125,125,125) }")
        self.selected_pushButton.setText("")
        self.selected_pushButton.setCheckable(False)
        self.selected_pushButton.setObjectName("selected_pushButton")
        self.horizontalLayout_13.addWidget(self.selected_pushButton)
        self.colorGroup_pushButton = QtGui.QPushButton(self.frame)
        self.colorGroup_pushButton.setMaximumSize(QtCore.QSize(30, 20))
        self.colorGroup_pushButton.setStyleSheet("QPushButton{ background-color: rgb(125,125,125) }")
        self.colorGroup_pushButton.setText("")
        self.colorGroup_pushButton.setChecked(False)
        self.colorGroup_pushButton.setObjectName("colorGroup_pushButton")
        self.horizontalLayout_13.addWidget(self.colorGroup_pushButton)
        self.fileName_LineEdit = QtGui.QLineEdit(self.frame)
        self.fileName_LineEdit.setMaximumSize(QtCore.QSize(200, 20))
        self.fileName_LineEdit.setObjectName("fileName_LineEdit")
        self.horizontalLayout_13.addWidget(self.fileName_LineEdit)
        self.filePath_LineEdit = QtGui.QLineEdit(self.frame)
        self.filePath_LineEdit.setMaximumSize(QtCore.QSize(16777215, 20))
        self.filePath_LineEdit.setObjectName("filePath_LineEdit")
        self.horizontalLayout_13.addWidget(self.filePath_LineEdit)
        self.setPath_pushButton = QtGui.QPushButton(self.frame)
        self.setPath_pushButton.setMaximumSize(QtCore.QSize(36, 20))
        self.setPath_pushButton.setStyleSheet("")
        self.setPath_pushButton.setCheckable(False)
        self.setPath_pushButton.setObjectName("setPath_pushButton")
        self.horizontalLayout_13.addWidget(self.setPath_pushButton)
        self.setExports_pushButton = QtGui.QPushButton(self.frame)
        self.setExports_pushButton.setMaximumSize(QtCore.QSize(16777215, 20))
        self.setExports_pushButton.setObjectName("setExports_pushButton")
        self.horizontalLayout_13.addWidget(self.setExports_pushButton)
        self.horizontalLayout_2.addLayout(self.horizontalLayout_13)
        self.horizontalLayout.addWidget(self.frame)

        self.retranslateUi(ModelExportEntry)
        QtCore.QMetaObject.connectSlotsByName(ModelExportEntry)

    def retranslateUi(self, ModelExportEntry):
        ModelExportEntry.setWindowTitle(QtGui.QApplication.translate("ModelExportEntry", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.setPath_pushButton.setText(QtGui.QApplication.translate("ModelExportEntry", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.setExports_pushButton.setText(QtGui.QApplication.translate("ModelExportEntry", "Set Exports", None, QtGui.QApplication.UnicodeUTF8))


# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_lts.ui'
#
# Created: Mon Apr 28 20:11:50 2014
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(673, 209)
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(20, 10, 131, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.layerCombo = QtGui.QComboBox(Dialog)
        self.layerCombo.setGeometry(QtCore.QRect(130, 10, 161, 22))
        self.layerCombo.setObjectName(_fromUtf8("layerCombo"))
        self.progress_bar = QtGui.QProgressBar(Dialog)
        self.progress_bar.setGeometry(QtCore.QRect(250, 60, 391, 23))
        self.progress_bar.setProperty("value", 24)
        self.progress_bar.setObjectName(_fromUtf8("progress_bar"))
        self.process_Button = QtGui.QPushButton(Dialog)
        self.process_Button.setGeometry(QtCore.QRect(18, 60, 211, 23))
        self.process_Button.setObjectName(_fromUtf8("process_Button"))
        self.find_cc_Button = QtGui.QPushButton(Dialog)
        self.find_cc_Button.setGeometry(QtCore.QRect(18, 160, 211, 23))
        self.find_cc_Button.setObjectName(_fromUtf8("find_cc_Button"))
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(20, 100, 91, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.lts_combo = QtGui.QComboBox(Dialog)
        self.lts_combo.setGeometry(QtCore.QRect(20, 120, 181, 22))
        self.lts_combo.setObjectName(_fromUtf8("lts_combo"))
        self.progressBar = QtGui.QProgressBar(Dialog)
        self.progressBar.setGeometry(QtCore.QRect(250, 160, 391, 23))
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.label.setText(_translate("Dialog", "Select Layer:", None))
        self.process_Button.setText(_translate("Dialog", "Calculate LTS", None))
        self.find_cc_Button.setText(_translate("Dialog", "Find Connected Components", None))
        self.label_2.setText(_translate("Dialog", "Select LTS Column", None))


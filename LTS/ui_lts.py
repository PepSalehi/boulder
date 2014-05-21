# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_lts.ui'
#
# Created: Wed May 21 16:50:12 2014
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
        Dialog.resize(673, 547)
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
        self.groupBox = QtGui.QGroupBox(Dialog)
        self.groupBox.setGeometry(QtCore.QRect(70, 230, 531, 271))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setGeometry(QtCore.QRect(40, 20, 101, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.road_combo = QtGui.QComboBox(self.groupBox)
        self.road_combo.setGeometry(QtCore.QRect(20, 40, 141, 22))
        self.road_combo.setObjectName(_fromUtf8("road_combo"))
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setGeometry(QtCore.QRect(40, 70, 111, 16))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.taz_combo = QtGui.QComboBox(self.groupBox)
        self.taz_combo.setGeometry(QtCore.QRect(20, 90, 141, 22))
        self.taz_combo.setObjectName(_fromUtf8("taz_combo"))
        self.label_5 = QtGui.QLabel(self.groupBox)
        self.label_5.setGeometry(QtCore.QRect(280, 30, 91, 16))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.label_6 = QtGui.QLabel(self.groupBox)
        self.label_6.setGeometry(QtCore.QRect(280, 60, 91, 16))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.label_7 = QtGui.QLabel(self.groupBox)
        self.label_7.setGeometry(QtCore.QRect(280, 90, 101, 16))
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.minDist = QtGui.QLineEdit(self.groupBox)
        self.minDist.setGeometry(QtCore.QRect(400, 30, 113, 20))
        self.minDist.setObjectName(_fromUtf8("minDist"))
        self.maxDist = QtGui.QLineEdit(self.groupBox)
        self.maxDist.setGeometry(QtCore.QRect(400, 60, 113, 20))
        self.maxDist.setObjectName(_fromUtf8("maxDist"))
        self.Detour_coeff = QtGui.QLineEdit(self.groupBox)
        self.Detour_coeff.setGeometry(QtCore.QRect(400, 90, 113, 20))
        self.Detour_coeff.setObjectName(_fromUtf8("Detour_coeff"))
        self.find_connectivity_btn = QtGui.QPushButton(self.groupBox)
        self.find_connectivity_btn.setGeometry(QtCore.QRect(170, 130, 171, 23))
        self.find_connectivity_btn.setObjectName(_fromUtf8("find_connectivity_btn"))
        self.progress_text = QtGui.QTextEdit(self.groupBox)
        self.progress_text.setGeometry(QtCore.QRect(150, 180, 231, 71))
        self.progress_text.setReadOnly(True)
        self.progress_text.setObjectName(_fromUtf8("progress_text"))
        self.label_8 = QtGui.QLabel(self.groupBox)
        self.label_8.setGeometry(QtCore.QRect(240, 160, 46, 13))
        self.label_8.setObjectName(_fromUtf8("label_8"))

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.label.setText(_translate("Dialog", "Select Layer:", None))
        self.process_Button.setText(_translate("Dialog", "Calculate LTS", None))
        self.find_cc_Button.setText(_translate("Dialog", "Find Islands", None))
        self.label_2.setText(_translate("Dialog", "Select LTS Column", None))
        self.groupBox.setTitle(_translate("Dialog", "Measure Connectivity", None))
        self.label_3.setText(_translate("Dialog", "Select Road Layer ", None))
        self.label_4.setText(_translate("Dialog", "Select TAZ Layer", None))
        self.label_5.setText(_translate("Dialog", "Minimum Distance", None))
        self.label_6.setText(_translate("Dialog", "Maximum Distance", None))
        self.label_7.setText(_translate("Dialog", "Detour Coefficient", None))
        self.find_connectivity_btn.setText(_translate("Dialog", "Compute Connectivity Measure", None))
        self.label_8.setText(_translate("Dialog", "Progress", None))


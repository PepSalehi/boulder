# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_test.ui'
#
# Created: Tue Apr 01 13:56:11 2014
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

class Ui_Test(object):
    def setupUi(self, Test):
        Test.setObjectName(_fromUtf8("Test"))
        Test.resize(571, 297)
        self.lineEdit_in = QtGui.QLineEdit(Test)
        self.lineEdit_in.setGeometry(QtCore.QRect(10, 110, 311, 20))
        self.lineEdit_in.setObjectName(_fromUtf8("lineEdit_in"))
        self.label = QtGui.QLabel(Test)
        self.label.setGeometry(QtCore.QRect(10, 80, 131, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.browse_in = QtGui.QPushButton(Test)
        self.browse_in.setGeometry(QtCore.QRect(450, 110, 75, 23))
        self.browse_in.setObjectName(_fromUtf8("browse_in"))
        self.progressBar = QtGui.QProgressBar(Test)
        self.progressBar.setGeometry(QtCore.QRect(30, 180, 511, 23))
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.label_2 = QtGui.QLabel(Test)
        self.label_2.setGeometry(QtCore.QRect(140, 0, 321, 81))
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.process_Button = QtGui.QPushButton(Test)
        self.process_Button.setGeometry(QtCore.QRect(250, 240, 75, 23))
        self.process_Button.setObjectName(_fromUtf8("process_Button"))

        self.retranslateUi(Test)
        QtCore.QMetaObject.connectSlotsByName(Test)

    def retranslateUi(self, Test):
        Test.setWindowTitle(_translate("Test", "Test", None))
        self.label.setText(_translate("Test", "Select shapefile:", None))
        self.browse_in.setText(_translate("Test", "Browse", None))
        self.label_2.setText(_translate("Test", "Compute Level of Traffic Stress", None))
        self.process_Button.setText(_translate("Test", "Process", None))


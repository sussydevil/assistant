#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(884, 694)
        MainWindow.setAutoFillBackground(False)
        self.CentralWidget = QtWidgets.QWidget(MainWindow)
        self.CentralWidget.setObjectName("CentralWidget")
        self.SensorGroupBox = QtWidgets.QGroupBox(self.CentralWidget)
        self.SensorGroupBox.setGeometry(QtCore.QRect(20, 10, 231, 371))
        font = QtGui.QFont()
        font.setFamily("Andale Mono")
        font.setPointSize(18)
        self.SensorGroupBox.setFont(font)
        self.SensorGroupBox.setCheckable(False)
        self.SensorGroupBox.setObjectName("SensorGroupBox")
        self.CLabelValue = QtWidgets.QLabel(self.SensorGroupBox)
        self.CLabelValue.setGeometry(QtCore.QRect(10, 320, 191, 31))
        font = QtGui.QFont()
        font.setFamily("Andale Mono")
        font.setPointSize(24)
        self.CLabelValue.setFont(font)
        self.CLabelValue.setObjectName("CLabelValue")
        self.PLabelValue = QtWidgets.QLabel(self.SensorGroupBox)
        self.PLabelValue.setGeometry(QtCore.QRect(10, 240, 191, 31))
        font = QtGui.QFont()
        font.setFamily("Andale Mono")
        font.setPointSize(24)
        self.PLabelValue.setFont(font)
        self.PLabelValue.setObjectName("PLabelValue")
        self.HLabelValue = QtWidgets.QLabel(self.SensorGroupBox)
        self.HLabelValue.setGeometry(QtCore.QRect(10, 160, 191, 31))
        font = QtGui.QFont()
        font.setFamily("Andale Mono")
        font.setPointSize(24)
        self.HLabelValue.setFont(font)
        self.HLabelValue.setObjectName("HLabelValue")
        self.TLabelValue = QtWidgets.QLabel(self.SensorGroupBox)
        self.TLabelValue.setGeometry(QtCore.QRect(10, 80, 191, 31))
        font = QtGui.QFont()
        font.setFamily("Andale Mono")
        font.setPointSize(24)
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(50)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.TLabelValue.setFont(font)
        self.TLabelValue.setTextFormat(QtCore.Qt.AutoText)
        self.TLabelValue.setObjectName("TLabelValue")
        self.TLabel = QtWidgets.QLabel(self.SensorGroupBox)
        self.TLabel.setGeometry(QtCore.QRect(10, 40, 131, 31))
        font = QtGui.QFont()
        font.setFamily("Andale Mono")
        font.setPointSize(18)
        font.setItalic(False)
        self.TLabel.setFont(font)
        self.TLabel.setObjectName("TLabel")
        self.PLabel = QtWidgets.QLabel(self.SensorGroupBox)
        self.PLabel.setGeometry(QtCore.QRect(10, 200, 121, 31))
        font = QtGui.QFont()
        font.setFamily("Andale Mono")
        font.setPointSize(18)
        self.PLabel.setFont(font)
        self.PLabel.setObjectName("PLabel")
        self.HLabel = QtWidgets.QLabel(self.SensorGroupBox)
        self.HLabel.setGeometry(QtCore.QRect(10, 120, 121, 31))
        font = QtGui.QFont()
        font.setFamily("Andale Mono")
        font.setPointSize(18)
        self.HLabel.setFont(font)
        self.HLabel.setObjectName("HLabel")
        self.CLabel = QtWidgets.QLabel(self.SensorGroupBox)
        self.CLabel.setGeometry(QtCore.QRect(10, 280, 121, 31))
        font = QtGui.QFont()
        font.setFamily("Andale Mono")
        font.setPointSize(18)
        self.CLabel.setFont(font)
        self.CLabel.setObjectName("CLabel")
        self.SensorSelectionComboBox = QtWidgets.QComboBox(self.CentralWidget)
        self.SensorSelectionComboBox.setGeometry(QtCore.QRect(440, 0, 211, 51))
        self.SensorSelectionComboBox.setObjectName("SensorSelectionComboBox")
        self.SensorSelectionLabel = QtWidgets.QLabel(self.CentralWidget)
        self.SensorSelectionLabel.setGeometry(QtCore.QRect(260, 10, 151, 31))
        font = QtGui.QFont()
        font.setFamily("Andale Mono")
        font.setPointSize(18)
        self.SensorSelectionLabel.setFont(font)
        self.SensorSelectionLabel.setObjectName("SensorSelectionLabel")
        self.ActionGroupBox = QtWidgets.QGroupBox(self.CentralWidget)
        self.ActionGroupBox.setGeometry(QtCore.QRect(280, 390, 591, 251))
        font = QtGui.QFont()
        font.setFamily("Andale Mono")
        font.setPointSize(18)
        self.ActionGroupBox.setFont(font)
        self.ActionGroupBox.setObjectName("ActionGroupBox")
        self.ActionListView = QtWidgets.QListView(self.ActionGroupBox)
        self.ActionListView.setEnabled(True)
        self.ActionListView.setGeometry(QtCore.QRect(10, 40, 571, 201))
        font = QtGui.QFont()
        font.setFamily("Andale Mono")
        font.setPointSize(14)
        self.ActionListView.setFont(font)
        self.ActionListView.setAutoFillBackground(False)
        self.ActionListView.setObjectName("ActionListView")
        self.RelayGroupBox = QtWidgets.QGroupBox(self.CentralWidget)
        self.RelayGroupBox.setGeometry(QtCore.QRect(10, 390, 241, 251))
        font = QtGui.QFont()
        font.setFamily("Andale Mono")
        font.setPointSize(18)
        self.RelayGroupBox.setFont(font)
        self.RelayGroupBox.setObjectName("RelayGroupBox")
        self.RelayOneCheckBox = QtWidgets.QCheckBox(self.RelayGroupBox)
        self.RelayOneCheckBox.setGeometry(QtCore.QRect(80, 50, 86, 20))
        self.RelayOneCheckBox.setObjectName("RelayOneCheckBox")
        self.RelayTwoCheckBox = QtWidgets.QCheckBox(self.RelayGroupBox)
        self.RelayTwoCheckBox.setGeometry(QtCore.QRect(80, 100, 86, 20))
        self.RelayTwoCheckBox.setObjectName("RelayTwoCheckBox")
        self.RelayThreeCheckBox = QtWidgets.QCheckBox(self.RelayGroupBox)
        self.RelayThreeCheckBox.setGeometry(QtCore.QRect(80, 150, 86, 20))
        self.RelayThreeCheckBox.setObjectName("RelayThreeCheckBox")
        self.RelayCommitButton = QtWidgets.QPushButton(self.RelayGroupBox)
        self.RelayCommitButton.setGeometry(QtCore.QRect(60, 190, 131, 41))
        font = QtGui.QFont()
        font.setFamily("Andale Mono")
        font.setPointSize(14)
        self.RelayCommitButton.setFont(font)
        self.RelayCommitButton.setObjectName("RelayCommitButton")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.CentralWidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(280, 40, 591, 341))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.ChartLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.ChartLayout.setContentsMargins(0, 0, 0, 0)
        self.ChartLayout.setObjectName("ChartLayout")
        MainWindow.setCentralWidget(self.CentralWidget)
        self.MenuBar = QtWidgets.QMenuBar(MainWindow)
        self.MenuBar.setGeometry(QtCore.QRect(0, 0, 884, 22))
        self.MenuBar.setObjectName("MenuBar")
        MainWindow.setMenuBar(self.MenuBar)
        self.StatusBar = QtWidgets.QStatusBar(MainWindow)
        self.StatusBar.setEnabled(True)
        self.StatusBar.setObjectName("StatusBar")
        MainWindow.setStatusBar(self.StatusBar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "???? ?????????????????????? ??????????????????"))
        self.SensorGroupBox.setTitle(_translate("MainWindow", "???????????? ?? ????????????????"))
        self.CLabelValue.setText(_translate("MainWindow", "Nan"))
        self.PLabelValue.setText(_translate("MainWindow", "Nan"))
        self.HLabelValue.setText(_translate("MainWindow", "Nan"))
        self.TLabelValue.setText(_translate("MainWindow", "Nan"))
        self.TLabel.setText(_translate("MainWindow", "??????????????????????"))
        self.PLabel.setText(_translate("MainWindow", "????????????????"))
        self.HLabel.setText(_translate("MainWindow", "??????????????????"))
        self.CLabel.setText(_translate("MainWindow", "?????????????? CO???"))
        self.SensorSelectionLabel.setText(_translate("MainWindow", "?????????? ??????????????", "123"))
        self.ActionGroupBox.setTitle(_translate("MainWindow", "??????????????"))
        self.RelayGroupBox.setTitle(_translate("MainWindow", "???????????????????? ????????????????????"))
        self.RelayOneCheckBox.setText(_translate("MainWindow", "???????? 1"))
        self.RelayTwoCheckBox.setText(_translate("MainWindow", "???????? 2"))
        self.RelayThreeCheckBox.setText(_translate("MainWindow", "???????? 3"))
        self.RelayCommitButton.setText(_translate("MainWindow", "??????????????????"))

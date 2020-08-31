# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/smcreator.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
import SoundMusic as sm


class Ui_MainWindow(QtWidgets.QWidget):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(689, 374)
        MainWindow.setStyleSheet("")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 10, 471, 131))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap("src\\../docs/SoundMusic.png"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(120, 170, 451, 21))
        self.lineEdit.setObjectName("lineEdit")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(80, 170, 31, 21))
        self.label_2.setObjectName("label_2")
        self.checkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox.setGeometry(QtCore.QRect(30, 270, 81, 20))
        self.checkBox.setObjectName("checkBox")
        self.checkBox_2 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_2.setGeometry(QtCore.QRect(580, 270, 81, 20))
        self.checkBox_2.setObjectName("checkBox_2")
        self.checkBox_3 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_3.setGeometry(QtCore.QRect(150, 270, 101, 20))
        self.checkBox_3.setObjectName("checkBox_3")
        self.checkBox_4 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_4.setGeometry(QtCore.QRect(300, 270, 101, 20))
        self.checkBox_4.setObjectName("checkBox_4")
        self.checkBox_5 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_5.setGeometry(QtCore.QRect(450, 270, 81, 20))
        self.checkBox_5.setObjectName("checkBox_5")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(580, 167, 93, 31))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.selectFile)
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(300, 320, 93, 28))
        self.pushButton_2.setStyleSheet("background-color: rgb(88, 142, 168)")
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.go)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(550, 10, 131, 61))
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setStyleSheet("color: rgb(88, 142, 168)")
        self.label_3.setObjectName("label_3")
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(580, 207, 93, 31))
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.clicked.connect(self.selectFit)
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(20, 210, 91, 21))
        self.label_4.setObjectName("label_4")
        self.lineEdit_2 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_2.setGeometry(QtCore.QRect(120, 210, 451, 21))
        self.lineEdit_2.setObjectName("lineEdit_2")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "SMCreator"))
        self.label_2.setText(_translate("MainWindow", "File:"))
        self.checkBox.setText(_translate("MainWindow", "MIDI"))
        self.checkBox_2.setText(_translate("MainWindow", "Sounds"))
        self.checkBox_3.setText(_translate("MainWindow", "Foreground"))
        self.checkBox_4.setText(_translate("MainWindow", "Background"))
        self.checkBox_5.setText(_translate("MainWindow", "Stereo"))
        self.pushButton.setText(_translate("MainWindow", "Search..."))
        self.pushButton_2.setText(_translate("MainWindow", "Go!"))
        self.label_3.setText(_translate("MainWindow", "Creator"))
        self.pushButton_3.setText(_translate("MainWindow", "Search..."))
        self.label_4.setText(_translate("MainWindow", "Fitness Model:"))

    def selectFile(self):
        fname,_ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', 
            '',"Audio files (*.wav *.mp3 *.aac *.flac)")
        if len(fname) > 0: self.lineEdit.setText(fname)

    def selectFit(self):
        fname,_ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', 
            '',"Fitness Model (*.svm)")
        if len(fname) > 0: self.lineEdit_2.setText(fname)

    def go(self):
        source = self.lineEdit.text()
        fit = self.lineEdit_2.text()
        if len(source) == 0 or len(fit) == 0: return

        midi = self.checkBox.isChecked()
        sounds = self.checkBox_2.isChecked()
        fg = self.checkBox_3.isChecked()
        bg = self.checkBox_4.isChecked()
        stereo = self.checkBox_5.isChecked()

        fname = QtWidgets.QFileDialog.getExistingDirectory(self, 'Save into', '')
        if len(fname) == 0: return

        if stereo: sm.generation.stereo(source, fname, fit, midi, fg, bg, sounds)
        else: sm.generation.mono(source, fname, fit, midi, fg, bg, sounds)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

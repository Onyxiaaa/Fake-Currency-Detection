import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QStackedWidget
from PyQt5.uic import loadUi

class Login(QMainWindow):
    def __init__(self):
        super(Login, self).__init__()
        loadUi("login.ui", self)
        self.btnLogin.clicked.connect(self.gotocreate)

    def gotocreate(self):
        createacc = CreateAcc()
        widget.addWidget(createacc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

class CreateAcc(QMainWindow):
    def __init__(self):
        super(CreateAcc, self).__init__()
        loadUi("gui.ui", self)

app = QApplication(sys.argv)
widget = QStackedWidget()
mainwindow = Login()
widget.addWidget(mainwindow)
# Mengatur ukuran jendela sesuai dengan ukuran GUI
widget.setFixedSize(mainwindow.size())
widget.show()
sys.exit(app.exec_())

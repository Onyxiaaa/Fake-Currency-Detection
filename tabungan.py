import re
import sys
from PyQt5 import QtWidgets, uic
import mysql.connector as mc
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
import random
import cv2
import numpy as np
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from matplotlib import pyplot as plt
from skimage.metrics import structural_similarity
import easyocr
from decimal import Decimal

qtcreator_file_login = "login.ui"  # Enter file here
Ui_LoginWindow, QtBaseClass = uic.loadUiType(qtcreator_file_login)

# Load the UI file for the main window
qtcreator_file_main = "gui.ui"  # Enter file here
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtcreator_file_main)


class LoginWindow(QMainWindow, Ui_LoginWindow):
    def __init__(self):
        super(LoginWindow, self).__init__()
        self.setupUi(self)
        self.btnLogin.clicked.connect(self.login)


    def login(self):
        username = self.txtUsername.text()
        password = self.txtPassword.text()
        if self.validate_login(username, password):
            # Close the login window and open the main window
            self.close()
            self.main_window = MainWindow()
            self.main_window.show()
        else:
            self.show_message("Error", "Invalid username or password")

    def validate_login(self, username, password):
        try:
            mydb = connect()
            mycursor = mydb.cursor()
            mycursor.execute("SELECT * FROM admin WHERE username = %s AND password = %s", (username, password))
            result = mycursor.fetchone()
            if result:
                return True
        except mc.Error as e:
            self.show_message("Error", f"Database error: {e}")
        return False

    def show_message(self, title, message):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.Image = None
        self.btnLoad.clicked.connect(self.fungsi)
        self.pushButton_2.clicked.connect(self.ssim)
        self.pushButton_3.clicked.connect(self.ssimcoin)

        # Event Setup
        self.btnCari.clicked.connect(self.search_data)  # Jika tombol cari diklik
        self.btnSimpan.clicked.connect(self.save_or_update_data)
        self.txtRekening.returnPressed.connect(
            self.search_data)  # Jika menekan tombol Enter saat berada di textbox Rekening
        self.btnClear.clicked.connect(self.clear_entry)
        self.btnHapus.clicked.connect(self.delete_data)
        self.edit_mode = ""
        self.btnHapus.setEnabled(False)  # Matikan tombol hapus
        self.btnHapus.setStyleSheet("color:black;background-color : grey")

        # Connect grid click signal
        self.gridNasabah.cellClicked.connect(self.grid_item_clicked)

        self.gridNasabah.setColumnWidth(0, 50)   # ID
        self.gridNasabah.setColumnWidth(1, 150)  # Nomor Rekening
        self.gridNasabah.setColumnWidth(2, 200)  # Nama
        self.gridNasabah.setColumnWidth(3, 250)  # Alamat
        self.gridNasabah.setColumnWidth(4, 150)  # Telepon
        self.gridNasabah.setColumnWidth(5, 200)  # Email
        self.gridNasabah.setColumnWidth(6, 120)  # Saldo
        self.gridNasabah.setColumnWidth(7, 100)  # Status
        self.select_data()


    def select_data(self):
        try:
            mydb = connect()
            mycursor = mydb.cursor()
            mycursor.execute("SELECT * FROM nasabah")
            result = mycursor.fetchall()

            self.gridNasabah.setHorizontalHeaderLabels(
                ['ID', 'Nomor Rekening', 'Nama', 'Alamat', 'Telepon', 'Email', 'Saldo', 'Status'])
            self.gridNasabah.setRowCount(0)

            for row_number, row_data in enumerate(result):
                self.gridNasabah.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    self.gridNasabah.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        except mc.Error as e:
            self.messagebox("ERROR", f"Terjadi kesalahan koneksi data: {e}")

    def search_data(self):
        try:
            mydb = connect()
            rekening = self.txtRekening.text()
            mycursor = mydb.cursor()
            mycursor.execute("SELECT * FROM nasabah WHERE rekening_nasabah=%s", (rekening,))
            result = mycursor.fetchone()
            if result:
                self.txtRekening.setText(str(result[1]))
                self.txtNama.setText(result[2])
                self.txtAlamat.setText(result[3])
                self.txtTelepon.setText(result[4])
                self.txtEmail.setText(result[5])
                self.cboStatus.setCurrentText(result[7])
                self.btnSimpan.setText("Update")
                self.edit_mode = True
                self.btnHapus.setEnabled(True)  # Aktifkan tombol hapus
                self.btnHapus.setStyleSheet("background-color : red")
            else:
                self.messagebox("INFO", "Data tidak ditemukan")
                self.txtNama.setFocus()
                self.btnSimpan.setText("Simpan")
                self.edit_mode = False
                self.btnHapus.setEnabled(False)  # Matikan tombol hapus
                self.btnHapus.setStyleSheet("color:black;background-color : grey")

        except mc.Error as e:
            self.messagebox("ERROR", f"Terjadi kesalahan koneksi data: {e}")

    def save_data(self):
        try:
            mydb = connect()
            rekening = random.randint(1000000, 9999999)  # Generate random account number
            nama = self.txtNama.text()
            alamat = self.txtAlamat.text()
            telepon = self.txtTelepon.text()
            email = self.txtEmail.text()
            status = self.cboStatus.currentText()
            mycursor = mydb.cursor()

            sql = "INSERT INTO nasabah (rekening_nasabah, nama_nasabah, alamat_nasabah, telepon_nasabah, email_nasabah, status) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (rekening, nama, alamat, telepon, email, status)
            mycursor.execute(sql, val)
            mydb.commit()

            if mycursor.rowcount > 0:
                self.messagebox("SUKSES", "Data Nasabah Tersimpan")
            else:
                self.messagebox("GAGAL", "Data Nasabah Gagal Tersimpan")

            self.clear_entry()  # Clear Entry Form
            self.select_data()  # Reload Datagrid

        except mc.Error as e:
            self.messagebox("ERROR", f"Terjadi kesalahan koneksi data: {e}")

    def update_data(self):
        try:
            mydb = connect()
            rekening = self.txtRekening.text()  # Assume the account number is already in the textbox
            nama = self.txtNama.text()
            alamat = self.txtAlamat.text()
            telepon = self.txtTelepon.text()
            email = self.txtEmail.text()
            status = self.cboStatus.currentText()
            mycursor = mydb.cursor()

            sql = "UPDATE nasabah SET nama_nasabah = %s, alamat_nasabah = %s, telepon_nasabah = %s, email_nasabah = %s, status = %s WHERE rekening_nasabah = %s"
            val = (nama, alamat, telepon, email, status, rekening)
            mycursor.execute(sql, val)
            mydb.commit()

            if mycursor.rowcount > 0:
                self.messagebox("SUKSES", "Data Nasabah Diperbarui")
            else:
                self.messagebox("GAGAL", "Data Nasabah Gagal Diperbarui")

            self.clear_entry()  # Clear Entry Form
            self.select_data()  # Reload Datagrid
            self.edit_mode = False

        except mc.Error as e:
            self.messagebox("ERROR", f"Terjadi kesalahan koneksi data: {e}")

    def save_or_update_data(self):
        if self.edit_mode:
            self.update_data()
        else:
            self.save_data()

    def delete_data(self):
        try:
            mydb = connect()
            rekening = self.txtRekening.text()
            mycursor = mydb.cursor()
            if self.edit_mode:
                sql = "DELETE FROM nasabah WHERE rekening_nasabah=%s"
                mycursor.execute(sql, (rekening,))
                mydb.commit()
                if mycursor.rowcount > 0:
                    self.messagebox("SUKSES", "Data Nasabah Dihapus")
                else:
                    self.messagebox("GAGAL", "Data Nasabah Gagal Dihapus")
                self.clear_entry()  # Clear Entry Form
                self.select_data()  # Reload Datagrid
                self.edit_mode = False
            else:
                self.messagebox("ERROR", "Sebelum menghapus data harus ditemukan dulu")
        except mc.Error as e:
            self.messagebox("ERROR", f"Terjadi kesalahan koneksi data: {e}")


    def clear_entry(self):
        self.txtRekening.setText("")
        self.txtNama.setText("")
        self.txtAlamat.setText("")
        self.txtTelepon.setText("")
        self.txtEmail.setText("")
        self.cboStatus.setCurrentText("")
        self.btnHapus.setEnabled(False)  # Matikan tombol hapus
        self.btnHapus.setStyleSheet("color:black;background-color : grey")
        self.btnSimpan.setText("Simpan")

    def messagebox(self, title, message):
        mess = QMessageBox()
        mess.setWindowTitle(title)
        mess.setText(message)
        mess.setStandardButtons(QMessageBox.Ok)
        mess.exec_()

    def grid_item_clicked(self, row, column):
        try:
            rekening = self.gridNasabah.item(row, 1).text()  # Ambil Nomor Rekening dari kolom ke-2 (indeks 1)
            mydb = connect()
            mycursor = mydb.cursor()
            mycursor.execute("SELECT * FROM nasabah WHERE rekening_nasabah = %s", (rekening,))
            result = mycursor.fetchone()
            if result:
                self.txtRekening.setText(str(result[1]))
                self.txtNama.setText(result[2])
                self.txtAlamat.setText(result[3])
                self.txtTelepon.setText(result[4])
                self.txtEmail.setText(result[5])
                self.cboStatus.setCurrentText(result[7])
                self.btnSimpan.setText("Update")
                self.edit_mode = True
                self.btnHapus.setEnabled(True)
                self.btnHapus.setStyleSheet("background-color: red")
            else:
                self.messagebox("INFO", "Data tidak ditemukan")
        except mc.Error as e:
            self.messagebox("ERROR", f"Terjadi kesalahan koneksi data: {e}")

    def loadImage(self, flname):
        self.Image = cv2.imread(flname)
        self.gambar = str(flname)
        self.displayImage(1)
        self.Image2 = self.Image

    def fungsi(self):
        flname,filter = QFileDialog.getOpenFileName(self,'Select Image', 'D:\\Pycham Project\\Pendeteksi Uang Palsu (2)\\Pendeteksi Uang Palsu\\foto\\', "Image Files(*.*)")
        if flname:
           self.loadImage(flname)
        else:
           print('Invalid Image')

    def crop_nominal(self):
        # Tentukan area croping dalam persentase
        x_percent = 0.0  # Persentase posisi x (pojok kiri atas)
        y_percent = 0.0  # Persentase posisi y (pojok kiri atas)
        w_percent = 0.5  # Persentase lebar area croping
        h_percent = 0.275  # Persentase tinggi area croping

        # Dapatkan dimensi gambar asli
        H, W = self.Image.shape[:2]

        # Hitung koordinat dan ukuran area croping berdasarkan persentase
        x = int(x_percent * W)
        y = int(y_percent * H)
        w = int(w_percent * W)
        h = int(h_percent * H)

        # Crop area nominal dari gambar
        cropped_nominal = self.Image[y:y + h, x:x + w]


        reader = easyocr.Reader(['en'])
        result = reader.readtext(cropped_nominal)

        for (bbox, text, prob) in result:
            print(text)

        nominal = text
        return nominal

    def coin(self):

        reader = easyocr.Reader(['en'])
        result = reader.readtext(self.Image)

        if not result:
            print("Tidak ada teks yang terdeteksi.")
        else:
            pattern = re.compile(r'^\d+$')
            print("Hanya angka yang terdeteksi:")
            for (bbox, text, prob) in result:
                if pattern.match(text):
                    print(f"Angka: {text}, Probabilitas: {prob}")
                    nominal = text
                else:
                    print(f"Teks non-angka ditemukan: {text}")

        return nominal

    def ssim(self):
        self.Image = cv2.cvtColor(self.Image, cv2.COLOR_BGR2GRAY)
        deteksi_nominal = self.crop_nominal()

        if deteksi_nominal == "100000":
            sample = cv2.imread('100000.jpg')
        elif deteksi_nominal == "50000":
            sample = cv2.imread('50000.jpg')
        elif deteksi_nominal == "20000":
            sample = cv2.imread('20000.jpg')
        elif deteksi_nominal == "10000":
            sample = cv2.imread('10000.jpg')
        elif deteksi_nominal == "5000":
            sample = cv2.imread('5000.jpeg')
        elif deteksi_nominal == "2000":
            sample = cv2.imread('2000.jpg')

        test = self.Image

        # konversi citra sample ke grayscale
        sample_gray = cv2.cvtColor(sample, cv2.COLOR_BGR2GRAY)

        # menghitung score ssim diantara 2 citra
        (score, diff) = structural_similarity(sample_gray, test, full=True)
        print("SSIM Score : ", score)

        # variable diff berfungsi untuk menyimpan perbedaan antara 2 citra
        # lalu dipresentasikan sebagai data float pada rentang array [0,1]
        # jadi array tersebut harus di ubah ke nilai integer 8 bit yang di masukan pada rentang array [0,255]
        # sebelum dapat di gunakan OpenCV
        diff = (diff * 255).astype("uint8")

        # Treshold perbedaan gambar tersebut
        # lalu mencari daerah kontur untuk 2 citra yang diinput
        thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if len(contours) == 2 else contours[1]

        # memasukan sample.shape dan datatype ke dalam mask
        # masukan test.copy ke dalam filled_after
        mask = np.zeros(sample.shape, dtype='uint8')
        filled_after = test.copy()

        # mencari objek dengan contour lalu membuat rectangle dan menggambarkanya pada objek tersebut
        for c in contours:
            area = cv2.contourArea(c)
            if area > 40:
                x, y, w, h = cv2.boundingRect(c)
                cv2.rectangle(sample, (x, y), (x + w, y + h), (36, 255, 12), 2)
                cv2.rectangle(test, (x, y), (x + w, y + h), (36, 255, 12), 2)
                cv2.drawContours(mask, [c], 0, (0, 255, 0), -1)
                cv2.drawContours(filled_after, [c], 0, (0, 266, 0), -1)

        # membuat output hasil menggunakan matplotlib
        fig, axs = plt.subplots(2, 2, figsize=(10, 7))

        axs[0, 0].imshow(sample_gray, cmap='gray')
        axs[0, 0].set_title('Sample')

        axs[0, 1].imshow(test, cmap='gray')
        axs[0, 1].set_title('Citra Pengujian')

        axs[1, 0].imshow(diff, cmap='gray')
        axs[1, 0].set_title('Perbedaan Menggunakan Negative Filter')

        axs[1, 1].imshow(mask, cmap='gray')
        axs[1, 1].set_title('Mask')

        for ax in axs.flat:
            ax.axis('off')

        plt.show()
        self.Image = filled_after
        self.displayImage(2)

        self.label_sim.setText(str("SSIM Score : ") + str(score))

        # jika skor kurang dari 0.97 persen, maka uang palsu jika lebih dari 0.97 maka uang asli
        if score < 0.97:
            print('Uang adalah Uang Palsu')
            self.label_keterangan.setText(str('Uang adalah Uang Palsu'))
        else:
            print('Uang adalah Uang Asli')
            self.label_keterangan.setText(str('Uang adalah Uang Asli'))
            self.update_saldo(deteksi_nominal)


    def ssimcoin(self):
        self.Image = cv2.cvtColor(self.Image, cv2.COLOR_BGR2GRAY)
        deteksi_nominal = self.coin()


        if deteksi_nominal == "500":
            sample = cv2.imread('500.jpeg')
        elif deteksi_nominal == "200":
            sample = cv2.imread('200.jpeg')

        test = self.Image

        # konversi citra sample ke grayscale
        sample_gray = cv2.cvtColor(sample, cv2.COLOR_BGR2GRAY)

        # menghitung score ssim diantara 2 citra
        (score, diff) = structural_similarity(sample_gray, test, full=True)
        print("SSIM Score : ", score)

        # variable diff berfungsi untuk menyimpan perbedaan antara 2 citra
        # lalu dipresentasikan sebagai data float pada rentang array [0,1]
        # jadi array tersebut harus di ubah ke nilai integer 8 bit yang di masukan pada rentang array [0,255]
        # sebelum dapat di gunakan OpenCV
        diff = (diff * 255).astype("uint8")

        # Treshold perbedaan gambar tersebut
        # lalu mencari daerah kontur untuk 2 citra yang diinput
        thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if len(contours) == 2 else contours[1]

        # memasukan sample.shape dan datatype ke dalam mask
        # masukan test.copy ke dalam filled_after
        mask = np.zeros(sample.shape, dtype='uint8')
        filled_after = test.copy()

        # mencari objek dengan contour lalu membuat rectangle dan menggambarkanya pada objek tersebut
        for c in contours:
            area = cv2.contourArea(c)
            if area > 40:
                x, y, w, h = cv2.boundingRect(c)
                cv2.rectangle(sample, (x, y), (x + w, y + h), (36, 255, 12), 2)
                cv2.rectangle(test, (x, y), (x + w, y + h), (36, 255, 12), 2)
                cv2.drawContours(mask, [c], 0, (0, 255, 0), -1)
                cv2.drawContours(filled_after, [c], 0, (0, 266, 0), -1)

        # membuat output hasil menggunakan matplotlib
        fig, axs = plt.subplots(2, 2, figsize=(10, 7))

        axs[0, 0].imshow(sample_gray, cmap='gray')
        axs[0, 0].set_title('Sample')

        axs[0, 1].imshow(test, cmap='gray')
        axs[0, 1].set_title('Citra Pengujian')

        axs[1, 0].imshow(diff, cmap='gray')
        axs[1, 0].set_title('Perbedaan Menggunakan Negative Filter')

        axs[1, 1].imshow(mask, cmap='gray')
        axs[1, 1].set_title('Mask')

        for ax in axs.flat:
            ax.axis('off')

        plt.show()
        self.Image = filled_after
        self.displayImage(2)

        self.label_sim.setText(str("SSIM Score : ") + str(score))

        # jika skor kurang dari 0.97 persen, maka uang palsu jika lebih dari 0.97 maka uang asli
        if score < 0.97:
            print('Uang adalah Uang Palsu')
            self.label_keterangan.setText(str('Uang adalah Uang Palsu'))
        else:
            print('Uang adalah Uang Asli')
            self.label_keterangan.setText(str('Uang adalah Uang Asli'))
            self.update_saldo(deteksi_nominal)

    def update_saldo(self, nominal):
        rekening = self.txtRekening.text()  # Ambil nomor rekening dari form
        mydb = connect()
        mycursor = mydb.cursor()

        # Ambil saldo terkini
        mycursor.execute("SELECT saldo FROM nasabah WHERE rekening_nasabah = %s", (rekening,))
        saldo = mycursor.fetchone()[0]

        if saldo is None:
            saldo = Decimal(0)

        # Update saldo
        saldo += Decimal(nominal)

        # Simpan perubahan saldo ke database
        sql = "UPDATE nasabah SET saldo = %s WHERE rekening_nasabah = %s"
        val = (saldo, rekening)
        mycursor.execute(sql, val)
        mydb.commit()
        self.select_data()


    def displayImage(self,windows=1):
        qformat = QImage.Format_Indexed8

        if len(self.Image.shape)==3:
            if(self.Image.shape[2])==4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888

        img = QImage(self.Image, self.Image.shape[1], self.Image.shape[0],
                     self.Image.strides[0], qformat)

        img = img.rgbSwapped()

        if windows == 1:
            self.label_input.setPixmap(QPixmap.fromImage(img))
            self.label_input.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            self.label_input.setScaledContents(True)

        if windows == 2:
            self.label_output.setPixmap(QPixmap.fromImage(img))
            self.label_output.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            self.label_output.setScaledContents(True)


def connect():
    try:
        mydb = mc.connect(
            host="localhost",
            user="root",
            password="",
            database="transaksi_elektronik"
        )
        return mydb
    except mc.Error as e:
        print(f"Terjadi kesalahan koneksi data: {e}")
        raise


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())

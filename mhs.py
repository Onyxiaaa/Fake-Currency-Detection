import sys
from PyQt5 import QtWidgets, uic
import mysql.connector as mc
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QMessageBox

qtcreator_file = "gui.ui"  # Enter file here.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtcreator_file)


class MyWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Event Setup
        self.btnCari.clicked.connect(self.search_data)  # Jika tombol cari diklik
        self.btnSimpan.clicked.connect(self.save_data)  # Jika tombol simpan diklik
        self.txtNIM.returnPressed.connect(self.search_data)  # Jika menekan tombol Enter saat berada di textbox NIM
        self.btnClear.clicked.connect(self.clear_entry)
        self.btnHapus.clicked.connect(self.delete_data)
        self.edit_mode = ""
        self.btnHapus.setEnabled(False)  # Matikan tombol hapus
        self.btnHapus.setStyleSheet("color:black;background-color : grey")

        # Connect grid click signal
        self.gridMahasiswa.cellClicked.connect(self.grid_item_clicked)

    def select_data(self):
        try:
            mydb = connect()
            mycursor = mydb.cursor()
            mycursor.execute("SELECT * FROM mahasiswa")
            result = mycursor.fetchall()

            self.gridMahasiswa.setHorizontalHeaderLabels(['ID', 'Nomor Rekening', 'Nama', 'Alamat', 'Telepon', 'Email', 'Saldo', 'Status'])
            self.gridMahasiswa.setRowCount(0)

            for row_number, row_data in enumerate(result):
                print(row_number)
                self.gridMahasiswa.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    self.gridMahasiswa.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        except mc.Error as e:
            self.messagebox("ERROR", f"Terjadi kesalahan koneksi data: {e}")

    def search_data(self):
        try:
            mydb = connect()
            nim = self.txtNIM.text()
            mycursor = mydb.cursor()
            mycursor.execute("SELECT * FROM mahasiswa where nim=%s", (nim,))
            result = mycursor.fetchone()
            if result:
                self.txtNama.setText(result[2])
                if result[3] == "L":
                    self.optLaki.setChecked(True)
                    self.optPerempuan.setChecked(False)
                else:
                    self.optLaki.setChecked(False)
                    self.optPerempuan.setChecked(True)
                self.cboProdi.setCurrentText(result[4])
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
            nim = self.txtNIM.text()
            nama = self.txtNama.text()
            jk = "L" if self.optLaki.isChecked() else "P"
            kode_prodi = self.cboProdi.currentText()
            mycursor = mydb.cursor()
            if not self.edit_mode:
                sql = "INSERT INTO mahasiswa (nim, nama, jk, kode_prodi) VALUES (%s, %s, %s, %s)"
                val = (nim, nama, jk, kode_prodi)
                mycursor.execute(sql, val)
                mydb.commit()
                if mycursor.rowcount > 0:
                    self.messagebox("SUKSES", "Data Mahasiswa Tersimpan")
                else:
                    self.messagebox("GAGAL", "Data Mahasiswa Gagal Tersimpan")
                self.clear_entry()  # Clear Entry Form
                self.select_data()  # Reload Datagrid
            elif self.edit_mode:
                sql = "UPDATE mahasiswa SET nama = %s, jk = %s, kode_prodi = %s WHERE nim = %s"
                val = (nama, jk, kode_prodi, nim)
                mycursor.execute(sql, val)
                mydb.commit()
                if mycursor.rowcount > 0:
                    self.messagebox("SUKSES", "Data Mahasiswa Diperbarui")
                else:
                    self.messagebox("GAGAL", "Data Mahasiswa Gagal Diperbarui")
                self.clear_entry()  # Clear Entry Form
                self.select_data()  # Reload Datagrid
            else:
                self.messagebox("ERROR", "Terjadi kesalahan Mode Edit")

        except mc.Error as e:
            self.messagebox("ERROR", f"Terjadi kesalahan koneksi data: {e}")

    def delete_data(self):
        try:
            mydb = connect()
            nim = self.txtNIM.text()
            mycursor = mydb.cursor()
            if self.edit_mode:
                sql = "DELETE FROM mahasiswa WHERE nim=%s"
                mycursor.execute(sql, (nim,))
                mydb.commit()
                if mycursor.rowcount > 0:
                    self.messagebox("SUKSES", "Data Mahasiswa Dihapus")
                else:
                    self.messagebox("GAGAL", "Data Mahasiswa Gagal Dihapus")
                self.clear_entry()  # Clear Entry Form
                self.select_data()  # Reload Datagrid
            else:
                self.messagebox("ERROR", "Sebelum meghapus data harus ditemukan dulu")
        except mc.Error as e:
            self.messagebox("ERROR", f"Terjadi kesalahan koneksi data: {e}")

    def clear_entry(self):
        self.txtNIM.setText("")
        self.txtNama.setText("")
        self.optLaki.setChecked(False)
        self.optPerempuan.setChecked(False)
        self.cboProdi.setCurrentText("")
        self.btnHapus.setEnabled(False)  # Matikan tombol hapus
        self.btnHapus.setStyleSheet("color:black;background-color : grey")

    def messagebox(self, title, message):
        mess = QMessageBox()
        mess.setWindowTitle(title)
        mess.setText(message)
        mess.setStandardButtons(QMessageBox.Ok)
        mess.exec_()

    def grid_item_clicked(self, row, column):
        try:
            nim = self.gridMahasiswa.item(row, 1).text()  # Ambil NIM dari kolom ke-2 (indeks 1)
            mydb = connect()
            mycursor = mydb.cursor()
            mycursor.execute("SELECT * FROM mahasiswa WHERE nim = %s", (nim,))
            result = mycursor.fetchone()
            if result:
                self.txtNIM.setText(result[1])
                self.txtNama.setText(result[2])
                if result[3] == "L":
                    self.optLaki.setChecked(True)
                    self.optPerempuan.setChecked(False)
                else:
                    self.optLaki.setChecked(False)
                    self.optPerempuan.setChecked(True)
                self.cboProdi.setCurrentText(result[4])
                self.btnSimpan.setText("Update")
                self.edit_mode = True
                self.btnHapus.setEnabled(True)
                self.btnHapus.setStyleSheet("background-color: red")
            else:
                self.messagebox("INFO", "Data tidak ditemukan")
        except mc.Error as e:
            self.messagebox("ERROR", f"Terjadi kesalahan koneksi data: {e}")


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
    window = MyWindow()
    window.show()
    window.select_data()
    sys.exit(app.exec_())

import os
import sys
import cv2
import numpy as np
from PIL import Image
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from matplotlib import pyplot as plt
from skimage.metrics import structural_similarity
import easyocr


class ShowImage(QMainWindow):
    def __init__(self):
        super(ShowImage, self).__init__()
        loadUi('ui.ui', self)
        self.Image = None
        self.actionLoad_Uang.triggered.connect(self.fungsi)
        self.pushButton.clicked.connect(self.grayscale)
        self.pushButton_4.clicked.connect(self.crop_nominal)

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

        cv2.imshow("Nominal",cropped_nominal)

        for (bbox, text, prob) in result:
            print(text)

    def grayscale(self):
        self.Image = cv2.cvtColor(self.Image, cv2.COLOR_BGR2GRAY)
        self.displayImage(2)

    # def ssim(self):
    #
    #
    #     test = self.Image
    #
    #     # konversi citra sample ke grayscale
    #     sample_gray = cv2.cvtColor(sample, cv2.COLOR_BGR2GRAY)
    #
    #     # menghitung score ssim diantara 2 citra
    #     (score, diff) = structural_similarity(sample_gray, test, full=True)
    #     print("SSIM Score : ", score)
    #
    #     # variable diff berfungsi untuk menyimpan perbedaan antara 2 citra
    #     # lalu dipresentasikan sebagai data float pada rentang array [0,1]
    #     # jadi array tersebut harus di ubah ke nilai integer 8 bit yang di masukan pada rentang array [0,255]
    #     # sebelum dapat di gunakan OpenCV
    #     diff = (diff * 255).astype("uint8")
    #
    #     # Treshold perbedaan gambar tersebut
    #     # lalu mencari daerah kontur untuk 2 citra yang diinput
    #     thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    #     contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #     contours = contours[0] if len(contours) == 2 else contours[1]
    #
    #     # memasukan sample.shape dan datatype ke dalam mask
    #     # masukan test.copy ke dalam filled_after
    #     mask = np.zeros(sample.shape, dtype='uint8')
    #     filled_after = test.copy()
    #
    #     # mencari objek dengan contour lalu membuat rectangle dan menggambarkanya pada objek tersebut
    #     for c in contours:
    #         area = cv2.contourArea(c)
    #         if area > 40:
    #             x, y, w, h = cv2.boundingRect(c)
    #             cv2.rectangle(sample, (x, y), (x + w, y + h), (36, 255, 12), 2)
    #             cv2.rectangle(test, (x, y), (x + w, y + h), (36, 255, 12), 2)
    #             cv2.drawContours(mask, [c], 0, (0, 255, 0), -1)
    #             cv2.drawContours(filled_after, [c], 0, (0, 266, 0), -1)
    #
    #     # membuat output hasil
    #     cv2.imshow('sample', sample_gray)
    #     cv2.imshow('citra pengujian', test)
    #     cv2.imshow('perbedaan menggunalan negative filter', diff)
    #     cv2.imshow('mask', mask)
    #     self.Image = filled_after
    #     self.displayImage(2)
    #
    #     self.label_3.setText(str("SSIM Score : ") + str(score))
    #
    #     # jika skor kurang dari 0.97 persen, maka uang palsu jika lebih dari 0.97 maka uang asli
    #     if score < 0.97:
    #         print('Uang adalah Uang Palsu')
    #         self.label_4.setText(str('Uang adalah Uang Palsu'))
    #     else:
    #         print('Uang adalah Uang Asli')
    #         self.label_4.setText(str('Uang adalah Uang Asli'))


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
            self.label.setPixmap(QPixmap.fromImage(img))
            self.label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            self.label.setScaledContents(True)

        if windows == 2:
            self.label_2.setPixmap(QPixmap.fromImage(img))
            self.label_2.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            self.label_2.setScaledContents(True)






app = QtWidgets.QApplication(sys.argv)
window = ShowImage()
window.setWindowTitle('Aplikasi Pendeteksi Uang Kertas Palsu')
window.show()
sys.exit(app.exec_())
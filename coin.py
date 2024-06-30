import easyocr
import cv2
import matplotlib.pyplot as plt
import re

# Membaca gambar
coin = cv2.imread("200.jpeg")
if coin is None:
    print("Gambar tidak ditemukan atau tidak dapat dibuka.")
else:
    # Konversi gambar ke grayscale
    coin_gray = cv2.cvtColor(coin, cv2.COLOR_BGR2GRAY)

    # Membuat objek EasyOCR reader
    reader = easyocr.Reader(['en'])

    # Mendapatkan hasil deteksi teks
    result = reader.readtext(coin_gray)

    if not result:
        print("Tidak ada teks yang terdeteksi.")
    else:
        pattern = re.compile(r'^\d+$')
        print("Hanya angka yang terdeteksi:")
        for (bbox, text, prob) in result:
            if pattern.match(text):
                print(f"Angka: {text}, Probabilitas: {prob}")
            else:
                print(f"Teks non-angka ditemukan: {text}")

        # Menampilkan gambar grayscale dengan bounding box dari hasil deteksi teks
        for (bbox, text, prob) in result:
            if pattern.match(text):
                # Draw the bounding box on the image
                (top_left, top_right, bottom_right, bottom_left) = bbox
                top_left = tuple(map(int, top_left))
                bottom_right = tuple(map(int, bottom_right))
                cv2.rectangle(coin_gray, top_left, bottom_right, (255, 255, 255), 2)

        # Display the grayscale image
        plt.figure(figsize=(10, 10))
        plt.imshow(coin_gray, cmap='gray')
        plt.title("Deteksi Angka pada Gambar Grayscale")
        plt.axis("off")
        plt.show()

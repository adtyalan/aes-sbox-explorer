# AES S-Box Explorer

![UNNES Logo](assets/unnes.png)

**AES S-Box Explorer** adalah aplikasi berbasis web yang dirancang untuk menghasilkan, menganalisis, dan menguji S-Box (Substitution Box) pada algoritma kriptografi AES (Advanced Encryption Standard).

Aplikasi ini menggunakan arsitektur *Client-Server*, di mana **FastAPI** bertindak sebagai backend untuk menangani logika kriptografi yang berat, dan **HTML/JavaScript** sebagai antarmuka pengguna yang interaktif.

## 📋 Fitur Utama

Aplikasi ini memiliki tiga modul utama:

### 1. S-Box Generator
Memungkinkan pengguna untuk membuat S-Box kustom berdasarkan parameter transformasi affine:
* **Affine Constant (C):** Konstanta aditif dalam transformasi affine.
* **Affine Matrix:** Eksplorasi matriks $8 \times 8$ di $GF(2)$ untuk menemukan S-Box yang valid (Bijektif).
* **Presets:** Menyediakan pilihan matriks dari referensi paper dan standar AES.
* **Random Generation:** Pembangkitan matriks affine acak yang invertible.

### 2. S-Box Analyzer
Menganalisis kekuatan kriptografis dari S-Box yang dihasilkan menggunakan metrik standar industri:
* **Non-Linearity (NL):** Mengukur ketahanan terhadap *Linear Cryptanalysis*.
* **SAC (Strict Avalanche Criterion):** Mengukur efek penyebaran bit.
* **BIC (Bit Independence Criterion):** Mengukur independensi antar bit output.
* **Differential Uniformity:** Mengukur ketahanan terhadap *Differential Cryptanalysis*.
* **Entropy & NPCR/UACI:** Analisis statistik untuk enkripsi citra.

### 3. AES Simulation
Menguji S-Box yang telah dibuat langsung pada proses enkripsi dan dekripsi AES-128:
* **Enkripsi Teks:** Input Plaintext dan Key, output Ciphertext (Hex).
* **Enkripsi Gambar:** Enkripsi file gambar (JPG/PNG) dengan visualisasi *noise* pada ciphertext.

## 🛠️ Teknologi yang Digunakan

* **Backend:** Python 3, FastAPI, Uvicorn
* **Frontend:** HTML5, CSS3, JavaScript (Fetch API)
* **Kriptografi & Komputasi:** NumPy, Pillow (PIL)
* **Logic:** Implementasi custom AES dan analisis S-Box (`sbox_logic.py`, `sbox_analysis.py`, `aes_cipher.py`)

## ⚙️ Instalasi

Pastikan Anda telah menginstal Python (versi 3.8 atau lebih baru).

1.  **Clone repositori ini:**
    ```bash
    git clone [https://github.com/adtyalan/aes-sbox-explorer.git](https://github.com/adtyalan/aes-sbox-explorer.git)
    cd aes-sbox-explorer
    ```

2.  **Buat Virtual Environment (Direkomendasikan):**
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # Mac/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instal Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *Pastikan `fastapi`, `uvicorn`, `numpy`, `pillow` ada di dalam `requirements.txt`.*

## 🚀 Cara Penggunaan

Langkah-langkah untuk menjalankan aplikasi:

1. **Jalankan Backend (API)**
      Buka terminal dan jalankan perintah berikut untuk menyalakan server FastAPI:
      ```bash
      uvicorn api:app --reload

2.  **Buka di Browser:**
    Akses alamat berikut di browser Anda (Chrome/Firefox/Edge):
    `http://127.0.0.1:5000` atau `http://localhost:5000`

3.  **Eksplorasi:**
    * Gunakan menu **Generator** untuk membuat S-Box baru.
    * Klik **Analyze** untuk melihat skor keamanannya.
    * Gunakan menu **Test Encryption** untuk mencoba mengenkripsi pesan rahasia menggunakan S-Box tersebut.

## 📂 Struktur File

* `app.py`: Entry point aplikasi web (Flask Controller).
* `api.py`: Endpoint API untuk komunikasi antara frontend dan logic backend.
* `sbox_logic.py`: Logika matematika untuk pembangkitan S-Box (Galois Field, Affine Transform).
* `sbox_analysis.py`: Algoritma untuk menghitung metrik analisis (Non-linearity, SAC, dll).
* `aes_cipher.py`: Implementasi algoritma AES (Encrypt/Decrypt) yang menggunakan S-Box dinamis.
* `index.html`: Antarmuka pengguna (Frontend).
* `assets/`: Folder untuk gambar statis (logo, dll).

## 🎓 Tentang Proyek

Proyek ini dikembangkan sebagai bagian dari penelitian/studi mengenai keamanan informasi dan kriptografi di **Universitas Negeri Semarang (UNNES)**. Fokus utama adalah memahami bagaimana modifikasi pada komponen non-linear (S-Box) mempengaruhi keamanan algoritma AES secara keseluruhan.

---
**Author:** 
* Ravinasa Deo
* Hanif Khaylila Fajri
* Akbar Nugroho Wisnu Murti
* Alan Aditya

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import numpy as np

# Import modul logika proyek Anda
import sbox_logic
import sbox_analysis
import aes_cipher

# Inisialisasi Aplikasi
app = FastAPI(title="AES S-Box Project API", version="1.0")

# Konfigurasi CORS (Agar Frontend HTML bisa mengakses API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ganti dengan domain spesifik jika di production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELS (Schema Data) ---


class MatrixRequest(BaseModel):
    matrix: List[List[int]]


class SBoxRequest(BaseModel):
    sbox: List[int]


class EncryptTextRequest(BaseModel):
    key: str
    plaintext: str
    sbox: List[int]


class DecryptTextRequest(BaseModel):
    key: str
    ciphertext_hex: str
    sbox: List[int]


class EncryptImageRequest(BaseModel):
    key: str
    image_hex: str  # Gambar dikirim sebagai Hex String
    sbox: List[int]


def calculate_entropy(data: bytes) -> float:
    """Menghitung Shannon Entropy dari bytes."""
    if not data:
        return 0.0

    # Hitung frekuensi setiap byte (0-255)
    counts = np.zeros(256)
    for byte in data:
        counts[byte] += 1

    probs = counts / len(data)
    # Hapus probabilitas 0 untuk menghindari log(0)
    probs = probs[probs > 0]

    entropy = -np.sum(probs * np.log2(probs))
    return entropy


def calculate_npcr_uaci(c1: bytes, c2: bytes) -> tuple:
    """
    Menghitung NPCR (Number of Pixels Change Rate) dan
    UACI (Unified Average Changing Intensity).
    """
    if len(c1) != len(c2):
        # Jika panjang beda (jarang terjadi di AES jika input sama panjang), potong ke min
        l = min(len(c1), len(c2))
        c1 = c1[:l]
        c2 = c2[:l]

    n = len(c1)
    if n == 0:
        return 0.0, 0.0

    # Convert ke numpy array untuk kecepatan
    arr1 = np.frombuffer(c1, dtype=np.uint8)
    arr2 = np.frombuffer(c2, dtype=np.uint8)

    # NPCR: Persentase pixel/byte yang berbeda
    diff = (arr1 != arr2).astype(int)
    npcr = (np.sum(diff) / n) * 100.0

    # UACI: Rata-rata intensitas perbedaan
    abs_diff = np.abs(arr1.astype(int) - arr2.astype(int))
    uaci = (np.sum(abs_diff) / (255 * n)) * 100.0

    return npcr, uaci


# --- ENDPOINTS ---


@app.get("/")
def root():
    return {"status": "running", "message": "Backend AES S-Box Siap!"}


@app.get("/presets")
def get_presets():
    """
    Step 1: Mengambil daftar matriks predefined.
    Menggabungkan matriks dari paper (sbox_logic.py) dengan matriks standar AES.
    """
    # 1. Ambil matriks dari file sbox_logic
    data = {k: v.tolist() for k, v in sbox_logic.PREDEFINED_MATRICES.items()}

    # 2. Tambahkan Matriks Affine Standar AES (Manual)
    # Sesuai definisi Affine Transformation di AES (FIPS 197)
    aes_standard_matrix = [
        [1, 0, 0, 0, 1, 1, 1, 1],
        [1, 1, 0, 0, 0, 1, 1, 1],
        [1, 1, 1, 0, 0, 0, 1, 1],
        [1, 1, 1, 1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 0, 0],
        [0, 0, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 1, 1, 1, 1, 1],
    ]

    # Masukkan ke dictionary agar muncul di dropdown Frontend
    data["AES Standard (Original)"] = aes_standard_matrix

    return data


@app.get("/random-matrix")
def get_random_matrix():
    """Step 1 Extra: Generate matriks acak yang valid (Invertible)."""
    try:
        matrix_np = sbox_logic.generate_random_affine_matrix()
        return {"matrix": matrix_np.tolist()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-sbox")
def generate_sbox(req: MatrixRequest):
    """Step 2: Konstruksi S-Box dari Matriks Affine"""
    try:
        matrix_np = np.array(req.matrix)
        sbox = sbox_logic.construct_sbox(matrix_np)
        return {"sbox": sbox}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze")
def analyze_sbox(req: SBoxRequest):
    """Step 3: Analisis Kriptografi S-Box"""
    sbox = req.sbox
    if len(sbox) != 256:
        raise HTTPException(status_code=400, detail="S-Box harus 256 elemen")

    try:
        # Hitung parameter menggunakan sbox_analysis.py
        nl = sbox_analysis.calculate_nl(sbox)
        sac = sbox_analysis.calculate_sac(sbox)
        bic_nl, bic_sac = sbox_analysis.calculate_bic(sbox)
        du, dap = sbox_analysis.calculate_du_dap(sbox)
        lap = sbox_analysis.calculate_lap(sbox)
        ad = sbox_analysis.calculate_ad(sbox)
        ci = sbox_analysis.calculate_ci(sbox)
        to = sbox_analysis.calculate_to(sbox)
        sv = sbox_analysis.calculate_sv(nl, sac, bic_nl, bic_sac)

        return {
            "nl": nl,
            "sac": sac,
            "bic_nl": bic_nl,
            "bic_sac": bic_sac,
            "du": du,
            "dap": dap,
            "lap": lap,
            "ad": ad,
            "ci": ci,
            "to": to,
            "sv": sv,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analisis: {str(e)}")


@app.post("/encrypt-text")
def encrypt_text(req: EncryptTextRequest):
    """Step 4/5: Enkripsi Teks"""
    if len(req.key) != 16:
        raise HTTPException(
            status_code=400, detail="Key harus tepat 16 karakter (128-bit)"
        )

    try:
        key_bytes = req.key.encode("utf-8")
        inv_sbox = sbox_logic.generate_inverse_sbox(req.sbox)
        cipher_hex = aes_cipher.encrypt_text(
            key_bytes, req.plaintext, req.sbox, inv_sbox
        )
        return {"ciphertext": cipher_hex}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/decrypt-text")
def decrypt_text(req: DecryptTextRequest):
    """Step 4/5: Dekripsi Teks"""
    if len(req.key) != 16:
        raise HTTPException(status_code=400, detail="Key harus tepat 16 karakter")

    try:
        key_bytes = req.key.encode("utf-8")
        inv_sbox = sbox_logic.generate_inverse_sbox(req.sbox)
        plaintext = aes_cipher.decrypt_text(
            key_bytes, req.ciphertext_hex, req.sbox, inv_sbox
        )
        return {"plaintext": plaintext}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Gagal dekripsi. Cek Key atau Ciphertext."
        )


@app.post("/process-image")
def process_image(req: EncryptImageRequest, mode: str = "encrypt"):
    """
    Step 4/5: Enkripsi/Dekripsi Gambar (Raw Bytes).
    Menerima dan mengembalikan data dalam format Hex String.
    """
    if len(req.key) != 16:
        raise HTTPException(status_code=400, detail="Key harus 16 karakter")

    try:
        key_bytes = req.key.encode("utf-8")
        inv_sbox = sbox_logic.generate_inverse_sbox(req.sbox)
        input_bytes = bytes.fromhex(req.image_hex)  # Konversi Hex -> Bytes

        if mode == "encrypt":
            # 1. Enkripsi Gambar Asli (C1)
            c1 = aes_cipher.encrypt_data(key_bytes, input_bytes, req.sbox, inv_sbox)

            # 2. Hitung Entropi C1
            entropy = calculate_entropy(c1)

            # 3. Avalanche Test untuk NPCR & UACI
            # Modifikasi 1 bit pada input (Plaintext Modified -> P2)
            input_array = bytearray(input_bytes)
            if len(input_array) > 0:
                input_array[0] ^= 1  # Flip LSB byte pertama

            # Enkripsi P2 -> C2
            c2 = aes_cipher.encrypt_data(
                key_bytes, bytes(input_array), req.sbox, inv_sbox
            )

            # Hitung NPCR & UACI antara C1 dan C2
            npcr, uaci = calculate_npcr_uaci(c1, c2)

            return {
                "result_hex": c1.hex(),
                "size": len(c1),
                "entropy": entropy,
                "npcr": npcr,
                "uaci": uaci,
            }
        else:
            result_bytes = aes_cipher.decrypt_data(
                key_bytes, input_bytes, req.sbox, inv_sbox
            )

        return {"result_hex": result_bytes.hex(), "size": len(result_bytes)}
    except ValueError:
        raise HTTPException(status_code=400, detail="Format Hex gambar tidak valid")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# FITUR BARU: UPLOAD S-BOX DARI EXCEL
# ============================================


@app.post("/upload-excel-sbox")
async def upload_excel_sbox(file: UploadFile = File(...)):
    """
    Upload S-Box dari file Excel.

    Menerima file Excel dengan format:
    - Single column: 256 nilai di kolom A
    - Single row: 256 nilai di baris 1
    - 16x16 Matrix: Matriks 16x16 standar S-Box

    Returns:
        {
            "success": bool,
            "sbox": List[int] (jika berhasil),
            "source_format": str,
            "validation": str,
            "message": str,
            "error": str (jika gagal)
        }
    """
    if not file.filename.endswith((".xlsx", ".xls", ".csv")):
        raise HTTPException(
            status_code=400, detail="Format file harus Excel (.xlsx, .xls) atau CSV"
        )

    try:
        # Baca file bytes
        file_bytes = await file.read()

        # Parse S-Box dari Excel
        sbox, source_format, error = sbox_logic.read_sbox_from_excel(file_bytes)

        if error:
            return {
                "success": False,
                "error": error,
                "message": "Gagal membaca S-Box dari Excel",
            }

        # Validasi S-Box
        is_valid, validation_msg = sbox_logic.validate_sbox(sbox)

        if not is_valid:
            return {
                "success": False,
                "error": validation_msg,
                "message": "S-Box tidak valid",
                "source_format": source_format,
            }

        # Jika valid, analisis S-Box
        try:
            nl = sbox_analysis.calculate_nl(sbox)
            sac = sbox_analysis.calculate_sac(sbox)
            dac = sbox_analysis.calculate_dac(sbox)
            pc = sbox_analysis.calculate_pc(sbox)
            bd = sbox_analysis.calculate_bd(sbox)

            analysis = {
                "nonlinearity": nl,
                "sac": round(float(sac), 4),
                "dac": round(float(dac), 4),
                "pc": round(float(pc), 4),
                "bd": int(bd),
            }
        except Exception as e:
            # Jika analisis gagal, tetap kembalikan S-Box (untuk demo/testing)
            analysis = {"error": f"Analisis partial: {str(e)}"}

        return {
            "success": True,
            "sbox": sbox,
            "source_format": source_format,
            "validation": validation_msg,
            "analysis": analysis,
            "message": f"S-Box berhasil diupload dari {source_format}",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error memproses file: {str(e)}")


# Jalankan terminal: uvicorn api:app --reload

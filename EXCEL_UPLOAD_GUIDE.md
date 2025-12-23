# Panduan Fitur Upload S-Box dari Excel

## 📋 Ringkasan Fitur

Fitur ini memungkinkan Anda untuk:

- ✅ **Upload S-Box** dari file Excel dalam berbagai format
- ✅ **Validasi otomatis** untuk memastikan S-Box valid (bijektif, 256 elemen)
- ✅ **Analisis cepat** S-Box yang diupload (Nonlinearity, SAC, DAC, dll)
- ✅ **Enkripsi & Dekripsi** menggunakan S-Box dari Excel

## 🎯 Cara Menggunakan

### Step 1: Persiapkan File Excel

File Excel harus memiliki 256 nilai S-Box dalam salah satu format berikut:

#### Format 1: Single Column (Rekomendasi)

- **Lokasi**: Kolom A (A1:A256)
- **Deskripsi**: Satu kolom berisi 256 nilai S-Box
- **Contoh**:
  ```
  A1: 99
  A2: 205
  A3: 85
  ...
  A256: 70
  ```

#### Format 2: Single Row

- **Lokasi**: Baris 1 (A1:IT1)
- **Deskripsi**: Satu baris berisi 256 nilai S-Box
- **Catatan**: 256 kolom dari A hingga IT

#### Format 3: 16x16 Matrix (Standard S-Box)

- **Lokasi**: Grid 16x16 (A1:P16)
- **Deskripsi**: S-Box disusun dalam matriks 4-bit x 4-bit
- **Contoh untuk S-Box 44**:
  ```
  Row 0:  99  205  85  71  25  127  113  219  63  244  109  159  11  228  94  214
  Row 1:  77  177  201  78  5   48   29   30   87   96   193  80   156  200  216  86
  ...
  Row 15: 164  69  41  230  104  47  144  251  20  17  150  225  254  161  102  70
  ```

### Step 2: Upload File

1. Di aplikasi, klik tombol **"Pilih File Excel"** (hijau)
2. Pilih file Excel dengan format yang sesuai
3. Tunggu hingga file diproses (akan muncul status "Sedang memproses...")

### Step 3: Validasi & Analisis

Sistem akan secara otomatis:

- ✓ Membaca dan memparse nilai S-Box
- ✓ Validasi bijektion (semua nilai 0-255 unik)
- ✓ Hitung metrik dasar (NL, SAC, DAC, PC, BD)
- ✓ Tampilkan hasil di UI

### Step 4: Gunakan S-Box

Klik tombol **"Gunakan S-Box Ini untuk Analisis"** untuk:

- Melanjutkan ke tab "Analisis Kriptografi"
- Melakukan enkripsi/dekripsi dengan S-Box tersebut
- Melihat laporan lengkap 10 metrik

## 🔍 Validasi S-Box

S-Box dinyatakan **VALID** jika:

1. ✅ Memiliki tepat **256 elemen**
2. ✅ Semua elemen adalah **integer 0-255**
3. ✅ **Bijektif**: Semua nilai **unik** (tidak ada duplikat)

Contoh S-Box **INVALID**:

- ❌ Hanya 200 elemen (kurang dari 256)
- ❌ Ada nilai di luar range 0-255
- ❌ Ada nilai yang muncul lebih dari 1 kali

## 📊 Metrik yang Ditampilkan

Setelah upload, Anda akan melihat analisis awal:

| Metrik  | Keterangan                       | Ideal  |
| ------- | -------------------------------- | ------ |
| **NL**  | Nonlinearity (resistensi linear) | ≥ 100  |
| **SAC** | Strict Avalanche Criterion       | ~0.5   |
| **DAC** | Differential Avalanche Criterion | ~0.5   |
| **PC**  | Propagation Criterion            | ~0.5   |
| **BD**  | Bit Dependency                   | Tinggi |

## 🛠️ API Endpoint

### `POST /upload-excel-sbox`

**Request:**

- **Content-Type**: `multipart/form-data`
- **Parameter**: `file` (Excel file)

**Response (Success):**

```json
{
  "success": true,
  "sbox": [99, 205, 85, ...],
  "source_format": "Single Column (256 values in column A)",
  "validation": "✓ S-Box Valid",
  "analysis": {
    "nonlinearity": 104,
    "sac": 0.5078,
    "dac": 0.4961,
    "pc": 0.5039,
    "bd": 256
  },
  "message": "S-Box berhasil diupload dari Single Column..."
}
```

**Response (Error):**

```json
{
  "success": false,
  "error": "S-Box harus memiliki 256 elemen",
  "message": "Gagal membaca S-Box dari Excel"
}
```

## 📁 Membuat File Excel Contoh

Gunakan script `create_sample_sbox_excel.py`:

```bash
python create_sample_sbox_excel.py
```

Output:

- `sample_sbox_column.xlsx` - Format kolom tunggal
- `sample_sbox_row.xlsx` - Format baris tunggal
- `sample_sbox_16x16.xlsx` - Format matriks 16x16

Ketiga file ini berisi S-Box-44 dari paper dan siap untuk diupload.

## ⚠️ Troubleshooting

### Error: "Pastikan server API sedang berjalan"

**Solusi**:

```bash
# Terminal 1: Jalankan Backend
uvicorn api:app --reload
```

### Error: "Format tidak dikenali"

**Solusi**: Pastikan file Excel memiliki format yang tepat:

- Format Kolom: 256 nilai di kolom A
- Format Baris: 256 nilai di baris 1
- Format Matriks: Grid 16x16

### Error: "S-Box tidak bijektif"

**Solusi**: Periksa file Excel:

- Pastikan semua nilai unik (tidak ada duplikat)
- Semua nilai dalam range 0-255
- Tidak ada nilai kosong atau text

## 🔒 Keamanan

- ✅ File tidak disimpan di server (hanya diproses di memory)
- ✅ Validasi ketat untuk memastikan data integritas
- ✅ API endpoint khusus untuk upload (tidak menimpa S-Box default)

## 📝 Catatan Teknis

### Dependencies Baru

```
openpyxl>=3.0.0  # Membaca .xlsx
pandas>=1.0.0    # Data processing
```

### Fungsi Backend (`sbox_logic.py`)

- `read_sbox_from_excel(file_bytes, sheet_name)` - Parse Excel ke S-Box
- `validate_sbox(sbox)` - Validasi struktur S-Box

### Fungsi Frontend (`index.html`)

- `handleExcelUpload(event)` - Handle file upload
- `useUploadedSBox()` - Gunakan S-Box uploaded

## 🚀 Fitur Masa Depan

Potensi pengembangan:

- ⬜ Support untuk multiple sheets Excel
- ⬜ Export hasil analisis ke Excel
- ⬜ Batch upload multiple S-Box
- ⬜ Komparasi antar S-Box
- ⬜ Visualisasi matrik S-Box dalam grafik

## 📚 Referensi

- Paper: "AES S-box modification uses affine matrices exploration..."
- Format Excel: Microsoft Office Open XML
- S-Box Standard: FIPS 197 (AES Specification)

---

**Created**: December 2025  
**Version**: 1.0  
**Status**: Stable

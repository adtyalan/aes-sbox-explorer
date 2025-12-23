import numpy as np

# Konstanta AES standar (CAES) = 0x63 (01100011) [cite: 196]
C_AES = np.array([1, 1, 0, 0, 0, 1, 1, 0])  # LSB first representation for vector calc

# Irreducible Polynomial: x^8 + x^4 + x^3 + x + 1 (0x11B) [cite: 13]
# Tabel Invers Multiplikatif AES (Standard) - Precomputed for efficiency
# Sesuai Table 1 pada paper [cite: 188]
AES_INVERSE_TABLE = [
    0x00,
    0x01,
    0x8D,
    0xF6,
    0xCB,
    0x52,
    0x7B,
    0xD1,
    0xE8,
    0x4F,
    0x29,
    0xC0,
    0xB0,
    0xE1,
    0xE5,
    0xC7,
    0x74,
    0xB4,
    0xAA,
    0x4B,
    0x99,
    0x2B,
    0x60,
    0x5F,
    0x58,
    0x3F,
    0xFD,
    0xCC,
    0xFF,
    0x40,
    0xEE,
    0xB2,
    0x3A,
    0x6E,
    0x5A,
    0xF1,
    0x55,
    0x4D,
    0xA8,
    0xC9,
    0xC1,
    0x0A,
    0x98,
    0x15,
    0x30,
    0x44,
    0xA2,
    0xC2,
    0x2C,
    0x45,
    0x92,
    0x6C,
    0xF3,
    0x39,
    0x66,
    0x42,
    0xF2,
    0x35,
    0x20,
    0x6F,
    0x77,
    0xBB,
    0x59,
    0x19,
    0x1D,
    0xFE,
    0x37,
    0x67,
    0x2D,
    0x31,
    0xF5,
    0x69,
    0xA7,
    0x64,
    0xAB,
    0x13,
    0x54,
    0x25,
    0xE9,
    0x09,
    0xED,
    0x5C,
    0x05,
    0xCA,
    0x4C,
    0x24,
    0x87,
    0xBF,
    0x18,
    0x3E,
    0x22,
    0xF0,
    0x51,
    0xEC,
    0x61,
    0x17,
    0x16,
    0x5E,
    0xAF,
    0xD3,
    0x49,
    0xA6,
    0x36,
    0x43,
    0xF4,
    0x47,
    0x91,
    0xDF,
    0x33,
    0x93,
    0x21,
    0x3B,
    0x79,
    0xB7,
    0x97,
    0x85,
    0x10,
    0xB5,
    0xBA,
    0x3C,
    0xB6,
    0x70,
    0xD0,
    0x06,
    0xA1,
    0xFA,
    0x81,
    0x82,
    0x83,
    0x7E,
    0x7F,
    0x80,
    0x96,
    0x73,
    0xBE,
    0x56,
    0x9B,
    0x9E,
    0x95,
    0xD9,
    0xF7,
    0x02,
    0xB9,
    0xA4,
    0xDE,
    0x6A,
    0x32,
    0x6D,
    0xD8,
    0x8A,
    0x84,
    0x72,
    0x2A,
    0x14,
    0x9F,
    0x88,
    0xF9,
    0xDC,
    0x89,
    0x9A,
    0xFB,
    0x7C,
    0x2E,
    0xC3,
    0x8F,
    0xB8,
    0x65,
    0x48,
    0x26,
    0xC8,
    0x12,
    0x4A,
    0xCE,
    0xE7,
    0xD2,
    0x62,
    0x0C,
    0xE0,
    0x1F,
    0xEF,
    0x11,
    0x75,
    0x78,
    0x71,
    0xA5,
    0x8E,
    0x76,
    0x3D,
    0xBD,
    0xBC,
    0x86,
    0x57,
    0x0B,
    0x28,
    0x2F,
    0xA3,
    0xDA,
    0xD4,
    0xE4,
    0x0F,
    0xA9,
    0x27,
    0x53,
    0x04,
    0x1B,
    0xFC,
    0xAC,
    0xE6,
    0x7A,
    0x07,
    0xAE,
    0x63,
    0xC5,
    0xDB,
    0xE2,
    0xEA,
    0x94,
    0x8B,
    0xC4,
    0xD5,
    0x9D,
    0xF8,
    0x90,
    0x6B,
    0xB1,
    0x0D,
    0xD6,
    0xEB,
    0xC6,
    0x0E,
    0xCF,
    0xAD,
    0x08,
    0x4E,
    0xD7,
    0xE3,
    0x5D,
    0x50,
    0x1E,
    0xB3,
    0x5B,
    0x23,
    0x38,
    0x34,
    0x68,
    0x46,
    0x03,
    0x8C,
    0xDD,
    0x9C,
    0x7D,
    0xA0,
    0xCD,
    0x1A,
    0x41,
    0x1C,
]

# S-Box 44 dari Makalah (Table 5) [cite: 1008]
# Digunakan sebagai "Golden Standard" jika pengguna memilih S-box terbaik
SBOX_44 = [
    99,
    205,
    85,
    71,
    25,
    127,
    113,
    219,
    63,
    244,
    109,
    159,
    11,
    228,
    94,
    214,
    77,
    177,
    201,
    78,
    5,
    48,
    29,
    30,
    87,
    96,
    193,
    80,
    156,
    200,
    216,
    86,
    116,
    143,
    10,
    14,
    54,
    169,
    148,
    68,
    49,
    75,
    171,
    157,
    92,
    114,
    188,
    194,
    121,
    220,
    131,
    210,
    83,
    135,
    250,
    149,
    253,
    72,
    182,
    33,
    190,
    141,
    249,
    82,
    232,
    50,
    21,
    84,
    215,
    242,
    180,
    198,
    168,
    167,
    103,
    122,
    152,
    162,
    145,
    184,
    43,
    237,
    119,
    183,
    7,
    12,
    125,
    55,
    252,
    206,
    235,
    160,
    140,
    133,
    179,
    192,
    110,
    176,
    221,
    134,
    19,
    6,
    187,
    59,
    26,
    129,
    112,
    73,
    175,
    45,
    24,
    218,
    44,
    66,
    151,
    32,
    137,
    31,
    35,
    147,
    236,
    247,
    117,
    132,
    79,
    136,
    154,
    105,
    199,
    101,
    203,
    52,
    57,
    4,
    153,
    197,
    88,
    76,
    202,
    174,
    233,
    62,
    208,
    91,
    231,
    53,
    1,
    124,
    0,
    28,
    142,
    170,
    158,
    51,
    226,
    65,
    123,
    186,
    239,
    246,
    38,
    56,
    36,
    108,
    8,
    126,
    9,
    189,
    81,
    234,
    212,
    224,
    13,
    3,
    40,
    64,
    172,
    74,
    181,
    118,
    39,
    227,
    130,
    89,
    245,
    166,
    16,
    61,
    106,
    196,
    211,
    107,
    229,
    195,
    138,
    18,
    93,
    207,
    240,
    95,
    58,
    255,
    209,
    217,
    15,
    111,
    46,
    173,
    223,
    42,
    115,
    238,
    139,
    243,
    23,
    98,
    100,
    178,
    37,
    97,
    191,
    213,
    222,
    155,
    165,
    2,
    146,
    204,
    120,
    241,
    163,
    128,
    22,
    90,
    60,
    185,
    67,
    34,
    27,
    248,
    164,
    69,
    41,
    230,
    104,
    47,
    144,
    251,
    20,
    17,
    150,
    225,
    254,
    161,
    102,
    70,
]

# ==========================================
# PREDEFINED AFFINE MATRICES FROM PAPER
# ==========================================

# K-44: The Proposed Best Matrix (Source: Page 11, Table source 1008)
# Ini adalah matriks yang menghasilkan S-Box 44 dengan skor terbaik.
K_44 = np.array(
    [
        [0, 1, 0, 1, 0, 1, 1, 1],
        [1, 0, 1, 0, 1, 0, 1, 1],
        [1, 1, 0, 1, 0, 1, 0, 1],
        [1, 1, 1, 0, 1, 0, 1, 0],
        [0, 1, 1, 1, 0, 1, 0, 1],
        [1, 0, 1, 1, 1, 0, 1, 0],
        [0, 1, 0, 1, 1, 1, 0, 1],
        [1, 0, 1, 0, 1, 1, 1, 0],
    ]
)

# K-18: Salah satu matriks eksplorasi (Source: Page 10, Source 862)
# Anda meminta K-18, berikut rekonstruksi dari data paper.
K_81 = np.array(
    [
        [1, 0, 1, 0, 0, 0, 0, 1],
        [1, 1, 0, 1, 0, 0, 0, 0],
        [0, 1, 1, 0, 1, 0, 0, 0],
        [0, 0, 1, 1, 0, 1, 0, 0],
        [0, 0, 0, 1, 1, 0, 1, 0],
        [0, 0, 0, 0, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 1, 1, 0],
        [0, 1, 0, 0, 0, 0, 1, 1],
    ]
)

# K-111: The Weakest/Comparison Matrix (Source: Page 9, Source 818)
# Digunakan dalam paper sebagai pembanding (skor S terburuk).
K_111 = np.array(
    [
        [1, 1, 0, 1, 1, 1, 0, 0],
        [0, 1, 1, 0, 1, 1, 1, 0],
        [0, 0, 1, 1, 0, 1, 1, 1],
        [1, 0, 0, 1, 1, 0, 1, 1],
        [1, 1, 0, 0, 1, 1, 0, 1],
        [1, 1, 1, 0, 0, 1, 1, 0],
        [0, 1, 1, 1, 0, 0, 1, 1],
        [1, 0, 1, 1, 1, 0, 0, 1],
    ]
)

K_128 = np.array(
    [
        [0, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 1, 1, 1, 1, 1, 1],
        [1, 1, 0, 1, 1, 1, 1, 1],
        [1, 1, 1, 0, 1, 1, 1, 1],
        [1, 1, 1, 1, 0, 1, 1, 1],
        [1, 1, 1, 1, 1, 0, 1, 1],
        [1, 1, 1, 1, 1, 1, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 0],
    ]
)


# Dictionary untuk memudahkan pemanggilan di App
PREDEFINED_MATRICES = {
    "K-44 (Best Proposed)": K_44,
    "K-81 (Exploration Sample)": K_81,
    "K-111 (Another Comparison)": K_111,
    "K-128 (Weak Comparison)": K_128,
}


def int_to_bit_array(n):
    """Mengubah integer (0-255) menjadi array bit (LSB di indeks 0)."""
    return np.array([(n >> i) & 1 for i in range(8)])


def bit_array_to_int(arr):
    """Mengubah array bit kembali ke integer."""
    res = 0
    for i in range(8):
        res |= int(arr[i]) << i
    return res


def generate_random_affine_matrix():
    """Membangkitkan matriks affine 8x8 secara acak (Step 1 Exploration)."""
    while True:
        # Generate matriks 8x8 random dengan nilai 0 atau 1
        matrix = np.random.randint(2, size=(8, 8))
        # Pastikan determinan tidak 0 (mod 2) agar invertible/bijektif
        det = int(round(np.linalg.det(matrix))) % 2
        if det != 0:
            return matrix


def construct_sbox(affine_matrix):
    """
    Step 2: Candidate S-box Construction.
    Rumus: B(x) = (K * X^-1 + C) mod 2

    """
    sbox = [0] * 256
    for x in range(256):
        # 1. Ambil invers multiplikatif dari x
        x_inv = AES_INVERSE_TABLE[x]

        # 2. Ubah ke bentuk vektor bit
        b_inv = int_to_bit_array(x_inv)

        # 3. Perkalian Matriks (Affine Transformation)
        # Matriks paper biasanya direpresentasikan bit 0 (LSB) di atas atau bawah tergantung notasi.
        # Disini kita gunakan perkalian dot product standar mod 2
        prod = np.dot(affine_matrix, b_inv) % 2

        # 4. Tambahkan Konstanta (XOR di GF(2))
        res_bits = (prod + C_AES) % 2

        # 5. Kembalikan ke integer
        sbox[x] = bit_array_to_int(res_bits)

    return sbox


def generate_inverse_sbox(sbox):
    """Membuat Invers S-Box untuk dekripsi."""
    inv_sbox = [0] * 256
    for i in range(256):
        inv_sbox[sbox[i]] = i
    return inv_sbox


def validate_sbox(sbox):
    """
    Validasi S-Box untuk memastikan:
    1. Panjang = 256
    2. Semua nilai adalah integer 0-255
    3. Bijektif (semua nilai unik)

    Returns: (is_valid: bool, error_message: str)
    """
    if not isinstance(sbox, (list, np.ndarray)):
        return False, "S-Box harus berupa list atau array"

    if len(sbox) != 256:
        return False, f"S-Box harus memiliki 256 elemen, ditemukan {len(sbox)}"

    try:
        sbox_int = [int(x) for x in sbox]
    except (ValueError, TypeError):
        return False, "Semua elemen S-Box harus berupa angka"

    if not all(0 <= x <= 255 for x in sbox_int):
        return False, "Semua elemen S-Box harus berada dalam range 0-255"

    if len(set(sbox_int)) != 256:
        return False, "S-Box harus bijektif (semua nilai unik, tidak ada duplikat)"

    return True, "✓ S-Box Valid"


def read_sbox_from_excel(file_bytes, sheet_name=0):
    """
    Membaca S-Box dari file Excel.

    Format yang diterima:
    - Single column: Satu kolom dengan 256 nilai (A1:A256)
    - Single row: Satu baris dengan 256 nilai (A1:IT1)
    - 16x16 matrix: Matriks 16x16 yang merepresentasikan S-Box

    Args:
        file_bytes: Bytes dari file Excel yang diupload
        sheet_name: Nama atau index sheet yang akan dibaca (default: 0 = sheet pertama)

    Returns:
        (sbox: list[int], source_format: str, error: str or None)
    """
    try:
        import io
        import pandas as pd

        # Baca Excel ke DataFrame
        excel_file = io.BytesIO(file_bytes)
        df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)

        # Coba deteksi format
        rows, cols = df.shape

        # Format 1: Single column (A1:A256)
        if cols == 1 and rows >= 256:
            sbox = df.iloc[:256, 0].dropna().tolist()
            sbox = [int(x) for x in sbox]
            if len(sbox) == 256:
                return sbox, "Single Column (256 values in column A)", None

        # Format 2: Single row (A1:IT1)
        if rows == 1 and cols >= 256:
            sbox = df.iloc[0, :256].dropna().tolist()
            sbox = [int(x) for x in sbox]
            if len(sbox) == 256:
                return sbox, "Single Row (256 values in row 1)", None

        # Format 3: 16x16 Matrix (S-Box dalam bentuk matriks 16x16)
        if rows >= 16 and cols >= 16:
            # Ambil 16x16 pertama
            matrix = df.iloc[:16, :16].values
            sbox = []
            for row in matrix:
                for val in row:
                    try:
                        sbox.append(int(val))
                    except (ValueError, TypeError):
                        pass

            if len(sbox) == 256:
                return sbox, "16x16 Matrix (standard S-Box format)", None

        # Jika tidak ada format yang cocok, coba flatten semua data
        all_values = df.values.flatten()
        all_values = [x for x in all_values if pd.notna(x)]

        if len(all_values) >= 256:
            try:
                sbox = [int(x) for x in all_values[:256]]
                return sbox, f"Flattened from {rows}x{cols} grid", None
            except (ValueError, TypeError):
                pass

        return (
            None,
            None,
            f"Format tidak dikenali. Pastikan Excel memiliki 256 nilai dalam format kolom, baris, atau matriks 16x16",
        )

    except Exception as e:
        return None, None, f"Error membaca Excel: {str(e)}"

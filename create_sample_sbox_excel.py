"""
Script untuk membuat file Excel contoh S-Box untuk testing
"""

import pandas as pd
import numpy as np
from sbox_logic import SBOX_44

# Format 1: Single Column (256 nilai di kolom A)
df_column = pd.DataFrame(SBOX_44)
df_column.to_excel(
    "sample_sbox_column.xlsx", index=False, header=False, sheet_name="SBox"
)
print("✓ Created: sample_sbox_column.xlsx (Single Column Format)")

# Format 2: Single Row (256 nilai di baris 1)
df_row = pd.DataFrame([SBOX_44])
df_row.to_excel("sample_sbox_row.xlsx", index=False, header=False, sheet_name="SBox")
print("✓ Created: sample_sbox_row.xlsx (Single Row Format)")

# Format 3: 16x16 Matrix (Standard S-Box Format)
matrix_2d = np.array(SBOX_44).reshape(16, 16)
df_matrix = pd.DataFrame(matrix_2d)
df_matrix.to_excel(
    "sample_sbox_16x16.xlsx", index=False, header=False, sheet_name="SBox"
)
print("✓ Created: sample_sbox_16x16.xlsx (16x16 Matrix Format)")

print("\n📝 Semua file contoh berhasil dibuat!")
print("Gunakan file-file ini untuk testing fitur upload Excel.")

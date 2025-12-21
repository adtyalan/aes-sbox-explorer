import streamlit as st
import numpy as np
import sbox_logic
import aes_cipher
import sbox_analysis
import io
from PIL import Image

st.set_page_config(page_title="Proyek Modifikasi S-Box AES", layout="wide")

st.title("Proyek Modifikasi S-Box AES dengan Eksplorasi Matriks Affine")
st.markdown("""
Aplikasi ini mengimplementasikan metode yang dijelaskan dalam makalah:
**"AES S-box modification uses affine matrices exploration for increased S-box strength"**.
""")

# Sidebar Navigasi
step = st.sidebar.radio("Tahapan Proyek:", 
    ["1. Affine Matrix Exploration", 
     "2. Candidate S-box Construction", 
     "3. S-box Candidate Testing", 
     "4. Final AES S-box Modification",
     "5. Implementasi Enkripsi & Dekripsi"])

if "current_sbox" not in st.session_state:
    # Default ke S-box 44 dari paper untuk awal
    st.session_state["current_sbox"] = sbox_logic.SBOX_44
if "affine_matrix" not in st.session_state:
    st.session_state["affine_matrix"] = None

# --- STEP 1: Affine Matrix Exploration ---
if step == "1. Affine Matrix Exploration":
    st.header("Step 1: Affine Matrix Exploration")
    st.markdown("""
    Berdasarkan paper, matriks affine adalah matriks $8 \\times 8$ di mana setiap elemen di $GF(2)$ bernilai 0 atau 1[cite: 247].
    Agar menghasilkan S-Box yang valid (Bijektif), matriks harus memiliki invers (determinannya tidak nol dalam mod 2)[cite: 13].
    """)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Pilih Metode Eksplorasi")
        # Tambahkan opsi "Input Manual"
        method = st.radio("Sumber Matriks:", ["Pilih dari Paper", "Input Manual", "Generate Random"])
        
        # --- OPSI 1: PILIH DARI PAPER ---
        if method == "Pilih dari Paper":
            matrix_choice = st.selectbox(
                "Pilih Matriks Affine:", 
                list(sbox_logic.PREDEFINED_MATRICES.keys())
            )
            
            if st.button("Gunakan Matriks Terpilih"):
                selected_matrix = sbox_logic.PREDEFINED_MATRICES[matrix_choice]
                st.session_state["affine_matrix"] = selected_matrix
                st.success(f"Matriks {matrix_choice} berhasil dipilih!")

        # --- OPSI 2: INPUT MANUAL (FITUR BARU) ---
        elif method == "Input Manual":
            st.info("Edit sel di bawah (hanya angka 0 atau 1).")
            
            # Inisialisasi matriks awal (Identitas) agar user tidak mengetik dari nol
            if "manual_input_matrix" not in st.session_state:
                st.session_state["manual_input_matrix"] = np.eye(8, dtype=int)

            # Tampilkan Editor Interaktif
            edited_matrix = st.data_editor(
                st.session_state["manual_input_matrix"], 
                key="matrix_editor",
                use_container_width=True,
                height=300
            )

            if st.button("Validasi & Gunakan Matriks Manual"):
                # Konversi ke NumPy array
                matrix_np = np.array(edited_matrix)
                
                # Cek apakah input hanya 0 dan 1
                if not np.all(np.isin(matrix_np, [0, 1])):
                    st.error("Error: Matriks hanya boleh berisi angka 0 atau 1!")
                else:
                    # Cek Determinan (Harus Ganjil/1 di mod 2 agar Invertible)
                    det = int(round(np.linalg.det(matrix_np))) % 2
                    if det == 0:
                        st.error("⚠️ Matriks ini TIDAK VALID (Singular/Tidak punya invers). S-Box yang dihasilkan tidak akan bijektif (akan ada nilai output yang hilang atau duplikat).")
                        # Kita tetap izinkan masuk session state agar user bisa melihat kegagalannya di Step 3
                        st.session_state["affine_matrix"] = matrix_np
                    else:
                        st.session_state["affine_matrix"] = matrix_np
                        st.success("✅ Matriks Valid (Invertible) dan Siap Digunakan!")

        # --- OPSI 3: RANDOM ---
        else: 
            if st.button("Generate Random Valid Affine Matrix"):
                matrix = sbox_logic.generate_random_affine_matrix()
                st.session_state["affine_matrix"] = matrix
                st.success("Matriks Affine Acak Berhasil Dibuat!")

    with col2:
        st.subheader("Visualisasi Matriks ($K$)")
        if st.session_state["affine_matrix"] is not None:
            st.write("Matriks Affine 8x8 Terpilih:")
            # Tampilkan matriks statis sebagai konfirmasi
            st.code(str(st.session_state["affine_matrix"]))
            
            # Info tambahan jika K-44
            if np.array_equal(st.session_state["affine_matrix"], sbox_logic.K_44):
                st.info("💡 **Info:** Ini adalah matriks K-44 (Best Proposed).")
        else:
            st.warning("Belum ada matriks yang dipilih.")

# --- STEP 2: Construction ---
elif step == "2. Candidate S-box Construction":
    st.header("Step 2: Candidate S-box Construction")
    st.markdown(r"""
    Kandidat S-Box dibangun menggunakan rumus:
    $$B(x) = (K \cdot X^{-1} + C_{AES}) \mod 2$$
    Dimana:
    - $K$: Matriks Affine dari Step 1.
    - $X^{-1}$: Invers multiplikatif di $GF(2^8)$.
    - $C_{AES}$: Konstanta 8-bit (0x63). 
    """)
    
    if st.button("Konstruksi S-Box dari Matriks Step 1"):
        if st.session_state["affine_matrix"] is None:
            st.error("Harap generate Matriks Affine di Step 1 terlebih dahulu!")
        else:
            new_sbox = sbox_logic.construct_sbox(st.session_state["affine_matrix"])
            st.session_state["current_sbox"] = new_sbox
            st.success("S-Box Kandidat Berhasil Dibuat!")
            
    st.subheader("Visualisasi S-Box Saat Ini:")
    st.write(np.array(st.session_state["current_sbox"]).reshape(16, 16))

# --- STEP 3: Testing ---
elif step == "3. S-box Candidate Testing":
    st.header("Step 3: S-box Candidate Testing")
    st.markdown("Pengujian S-Box dengan parameter kriptografi lengkap.")
    
    if st.button("Jalankan Analisis Lengkap"):
        sbox = st.session_state["current_sbox"]
        
        with st.spinner("Menghitung parameter kriptografi..."):
            # 1. Basic
            unique_vals = len(set(sbox))
            is_bijective = (unique_vals == 256)
            
            # 2. Advanced Metrics
            nl = sbox_analysis.calculate_nl(sbox)
            sac = sbox_analysis.calculate_sac(sbox)
            bic_nl, bic_sac = sbox_analysis.calculate_bic(sbox) # Memastikan sbox_analysis.py sudah update
            du, dap = sbox_analysis.calculate_du_dap(sbox)
            lap = sbox_analysis.calculate_lap(sbox)
            ad = sbox_analysis.calculate_ad(sbox)
            ci = sbox_analysis.calculate_ci(sbox)
            sv = sbox_analysis.calculate_sv(nl, sac, bic_nl, bic_sac)
        
        # Display Results
        st.subheader("Hasil Analisis")
        
        # Kita bagi menjadi 4 kolom atau menyusun ulang agar muat
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("Kriteria Dasar")
            st.metric("Bijectivity", "Yes" if is_bijective else "No")
            st.metric("Nonlinearity (NL)", f"{nl}", help="Target: 112 (AES)")
            st.metric("Corr. Immunity (CI)", f"{ci}")

        with col2:
            st.info("Kriteria Avalanche")
            st.metric("SAC", f"{sac:.5f}", help="Ideal: 0.5")
            st.metric("BIC-NL", f"{bic_nl:.2f}", help="Ideal: Tinggi (~112)")
            st.metric("BIC-SAC", f"{bic_sac:.5f}", help="Ideal: 0.5")
            st.metric("Strength Value (SV)", f"{sv:.4f}", help="Formula Paper: Semakin kecil (dekat 0) semakin baik.")

        with col3:
            st.info("Ketahanan Serangan")
            st.metric("Diff. Uniformity (DU)", f"{du}", help="Ideal: 4 (AES)")
            st.metric("DAP", f"{dap:.6f}", help="Differential Approximation Probability") # DAP ditambahkan kembali
            st.metric("LAP", f"{lap:.6f}", help="Linear Approximation Probability")
            st.metric("Alg. Degree (AD)", f"{ad}", help="Ideal: 7") # AD tetap ada
            
        # Interpretasi Singkat
        st.markdown("---")
        # Logika scoring sederhana
        score_sac = abs(sac - 0.5)
        score_bicsac = abs(bic_sac - 0.5)
        
        if nl >= 112 and du <= 4 and score_sac < 0.01 and score_bicsac < 0.01:
            st.success("🌟 **EXCELLENT S-BOX**: S-Box ini memenuhi standar keamanan AES dan Paper.")
        elif nl >= 100:
            st.warning("⚠️ **GOOD S-BOX**: Cukup kuat, namun belum optimal di beberapa parameter.")
        else:
            st.error("❌ **WEAK S-BOX**: S-Box lemah, rentan terhadap serangan.")

# --- STEP 4: Final Modification ---
elif step == "4. Final AES S-box Modification":
    st.header("Step 4: Final AES S-box Modification")
    st.markdown("""
    [cite_start]Berdasarkan makalah, **S-box 44** adalah yang terbaik dengan nilai Nonlinearity 112 dan SAC 0.50073[cite: 21, 1385]. 
    Di sini Anda dapat memilih untuk menggunakan S-Box hasil eksplorasi matriks Anda sebelumnya atau memuat **S-box 44** asli dari makalah untuk perbandingan.
    """)
    
    # Tombol aksi
    if st.button("Gunakan S-Box 44 (Terbaik dari Paper)"):
        st.session_state["current_sbox"] = sbox_logic.SBOX_44
        st.success("S-Box 44 Dimuat sebagai S-Box Aktif!")
            
    # Visualisasi Tabel Penuh
    st.subheader("Visualisasi S-Box Aktif Saat Ini:")
    st.markdown("Berikut adalah tabel S-Box penuh ($16 \\times 16$) yang akan digunakan untuk proses enkripsi/dekripsi:")
    
    # Menampilkan array S-Box dalam format grid 16x16
    sbox_grid = np.array(st.session_state["current_sbox"]).reshape(16, 16)
    st.write(sbox_grid)
    
# --- STEP 5: Implementasi Enkripsi & Dekripsi ---
elif step == "5. Implementasi Enkripsi & Dekripsi":
    st.header("Implementasi Enkripsi & Dekripsi")
    st.markdown("Menggunakan algoritma AES yang dimodifikasi dengan S-Box terpilih.")

    # Input Kunci Global
    key_input = st.text_input("Masukkan Kunci (Key) 16 karakter:", "KunciRahasia1234")
    
    if len(key_input) != 16:
        st.warning("⚠️ Kunci harus tepat 16 karakter (128-bit).")
    else:
        key_bytes = key_input.encode('utf-8')
        sbox = st.session_state["current_sbox"]
        inv_sbox = sbox_logic.generate_inverse_sbox(sbox)

        # Tab Selection
        tab1, tab2 = st.tabs(["📝 Enkripsi Teks", "🖼️ Enkripsi Gambar"])

        # === TAB 1: TEKS ===
        with tab1:
            st.subheader("Enkripsi Teks")
            col1, col2 = st.columns(2)
            
            with col1:
                text_input = st.text_area("Plaintext:", "Ini adalah pesan rahasia.")
                if st.button("Enkripsi Teks"):
                    try:
                        cipher_hex = aes_cipher.encrypt_text(key_bytes, text_input, sbox, inv_sbox)
                        st.session_state["text_cipher"] = cipher_hex
                        st.success("Teks Terenkripsi!")
                    except Exception as e:
                        st.error(f"Error: {e}")
                
                if "text_cipher" in st.session_state:
                    st.text_area("Ciphertext (Hex):", st.session_state["text_cipher"], height=100)

            with col2:
                cipher_input = st.text_input("Input Hex untuk Dekripsi:", 
                                            value=st.session_state.get("text_cipher", ""))
                if st.button("Dekripsi Teks"):
                    try:
                        plain_text = aes_cipher.decrypt_text(key_bytes, cipher_input, sbox, inv_sbox)
                        st.success("Teks Terdekripsi!")
                        st.code(plain_text)
                    except Exception as e:
                        st.error("Gagal mendekripsi.")

        # === TAB 2: GAMBAR ===
        with tab2:
            st.subheader("Enkripsi Gambar")
            st.warning("⚠️ Catatan: Karena implementasi ini menggunakan Python murni, proses akan lambat untuk gambar besar. Gambar akan otomatis di-resize ke lebar 100px untuk demo.")

            uploaded_file = st.file_uploader("Upload Gambar (JPG/PNG)", type=["jpg", "png", "jpeg"])

            if uploaded_file is not None:
                # 1. Baca dan Resize Gambar
                image = Image.open(uploaded_file)
                
                # Resize agar cepat (Max width 100px)
                base_width = 100
                w_percent = (base_width / float(image.size[0]))
                h_size = int((float(image.size[1]) * float(w_percent)))
                image_small = image.resize((base_width, h_size), Image.Resampling.LANCZOS)
                
                # Konversi ke Bytes
                img_byte_arr = io.BytesIO()
                # Kita simpan sebagai PNG atau format asli untuk menjaga data pixel
                fmt = image.format if image.format else 'PNG'
                image_small.save(img_byte_arr, format=fmt)
                img_bytes = img_byte_arr.getvalue()

                st.image(image_small, caption=f"Original (Resized: {image_small.size})", width=200)

                if st.button("Enkripsi Gambar"):
                    with st.spinner("Sedang mengenkripsi pixel..."):
                        # ENKRIPSI
                        encrypted_data = aes_cipher.encrypt_data(key_bytes, img_bytes, sbox, inv_sbox)
                        st.session_state["img_cipher"] = encrypted_data
                        st.success(f"Enkripsi Selesai! Ukuran data: {len(encrypted_data)} bytes")

                # Tampilkan Hasil Enkripsi (Visualisasi Noise)
                if "img_cipher" in st.session_state:
                    enc_bytes = st.session_state["img_cipher"]
                    
                    # Visualisasi Data Terenkripsi sebagai Gambar Noise
                    # Kita mencoba mengubah bytes acak menjadi gambar grayscale
                    # Hitung dimensi kotak untuk visualisasi
                    import math
                    size_side = int(math.sqrt(len(enc_bytes)))
                    # Potong data agar pas kotak
                    viz_data = enc_bytes[:size_side*size_side]
                    
                    try:
                        noise_img = Image.frombytes('L', (size_side, size_side), viz_data)
                        st.image(noise_img, caption="Visualisasi Ciphertext (Noise)", width=200)
                        st.caption("Gambar di atas adalah representasi visual dari data terenkripsi. Tidak ada pola gambar asli yang terlihat.")
                    except:
                        st.warning("Tidak dapat memvisualisasikan bytes terenkripsi.")

                    # Tombol Dekripsi
                    if st.button("Dekripsi Kembali ke Gambar Asli"):
                        with st.spinner("Sedang mendekripsi..."):
                            try:
                                # DEKRIPSI
                                decrypted_data = aes_cipher.decrypt_data(key_bytes, enc_bytes, sbox, inv_sbox)
                                
                                # Reconstruct Image
                                decrypted_io = io.BytesIO(decrypted_data)
                                decrypted_image = Image.open(decrypted_io)
                                
                                st.image(decrypted_image, caption="Hasil Dekripsi Sukses", width=200)
                                st.success("Gambar berhasil dikembalikan utuh!")
                            except Exception as e:
                                st.error(f"Gagal mendekripsi: {e}")
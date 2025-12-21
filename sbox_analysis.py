import numpy as np

def walsh_hadamard_transform(f):
    """Menghitung Walsh-Hadamard Transform (WHT) dari fungsi boolean f."""
    n = len(f)
    w = f.copy()
    h = 1
    while h < n:
        for i in range(0, n, h * 2):
            for j in range(i, i + h):
                x = w[j]
                y = w[j + h]
                w[j] = x + y
                w[j + h] = x - y
        h *= 2
    return w

def get_bit_components(sbox):
    """Memecah S-Box menjadi 8 fungsi boolean (koordinat)."""
    n = len(sbox)
    components = []
    for i in range(8):
        # Ambil bit ke-i dari setiap output S-Box
        comp = np.array([(x >> i) & 1 for x in sbox])
        components.append(comp)
    return components

def calculate_nl(sbox):
    """Menghitung Nonlinearity (NL)."""
    components = get_bit_components(sbox)
    n = 8
    min_nl = 255
    
    for f in components:
        f_signed = np.where(f == 0, 1, -1)
        spectrum = walsh_hadamard_transform(f_signed)
        max_abs_wht = np.max(np.abs(spectrum))
        nl = (2**(n-1)) - (max_abs_wht / 2)
        if nl < min_nl:
            min_nl = nl
            
    return int(min_nl)

def calculate_sac(sbox):
    """Menghitung Strict Avalanche Criterion (SAC) global."""
    n = 8
    total_sac = 0
    count = 0
    
    for i in range(n):
        input_mask = 1 << i
        change_count = 0
        total_pairs = 0
        
        for x in range(256):
            y1 = sbox[x]
            y2 = sbox[x ^ input_mask]
            diff = y1 ^ y2
            hw = bin(diff).count('1')
            change_count += hw
            total_pairs += 1
            
        avg_change = change_count / (total_pairs * n)
        total_sac += avg_change
        count += 1
        
    return total_sac / count

# --- FUNGSI BARU/UPDATED UNTUK BIC-SAC ---
def calculate_sac_of_function(f):
    """
    Helper: Menghitung SAC untuk satu fungsi boolean f.
    Digunakan di dalam perhitungan BIC-SAC.
    """
    n = 8
    total_sac = 0
    
    for i in range(n): # Bit input ke-i diflip
        input_mask = 1 << i
        flip_count = 0
        
        for x in range(256):
            y1 = f[x]
            y2 = f[x ^ input_mask]
            if y1 != y2:
                flip_count += 1
                
        # Probabilitas bit output berubah (Ideal 0.5)
        prob = flip_count / 256.0
        total_sac += prob
        
    return total_sac / n

def calculate_bic(sbox):
    """
    Menghitung Bit Independence Criterion (BIC).
    Output: Tuple (BIC-NL, BIC-SAC)
    """
    components = get_bit_components(sbox)
    n = 8
    
    sum_bic_nl = 0
    sum_bic_sac = 0
    pair_count = 0
    
    for i in range(n):
        for j in range(i + 1, n):
            # XOR dua komponen fungsi output
            h = components[i] ^ components[j]
            
            # 1. Hitung NL untuk h (BIC-NL)
            h_signed = np.where(h == 0, 1, -1)
            spectrum = walsh_hadamard_transform(h_signed)
            nl = (2**(n-1)) - (np.max(np.abs(spectrum)) / 2)
            sum_bic_nl += nl
            
            # 2. Hitung SAC untuk h (BIC-SAC)
            # Pastikan fungsi helper 'calculate_sac_of_function' sudah ada di atas
            sac_val = calculate_sac_of_function(h)
            sum_bic_sac += sac_val
            
            pair_count += 1
            
    avg_bic_nl = sum_bic_nl / pair_count
    avg_bic_sac = sum_bic_sac / pair_count
    
    return avg_bic_nl, avg_bic_sac
# ---------------------------------------------

def calculate_du_dap(sbox):
    """Menghitung Differential Uniformity (DU) dan DAP."""
    n = 256
    ddt = np.zeros((n, n), dtype=int)
    
    for input_diff in range(1, n):
        for x in range(n):
            y1 = sbox[x]
            y2 = sbox[x ^ input_diff]
            output_diff = y1 ^ y2
            ddt[input_diff][output_diff] += 1
            
    du = int(np.max(ddt))
    dap = du / n
    return du, dap

def calculate_lap(sbox):
    """Menghitung Linear Approximation Probability (LAP)."""
    n = 8
    max_bias = 0
    components = get_bit_components(sbox)
    
    for i in range(1, 256): 
        f_comb = np.zeros(256, dtype=int)
        for bit in range(8):
            if (i >> bit) & 1:
                f_comb ^= components[bit]
        
        f_signed = np.where(f_comb == 0, 1, -1)
        spectrum = walsh_hadamard_transform(f_signed)
        
        current_max = np.max(np.abs(spectrum))
        # Bias standar = MaxCorrelation / 2^(n+1) -> di sini kita pakai MaxCorr / 512
        this_lap = (current_max) / 512 
        if this_lap > max_bias:
            max_bias = this_lap
            
    return max_bias

def algebraic_normal_form(f):
    """Helper ANF."""
    n = len(f)
    anf = f.copy()
    h = 1
    while h < n:
        for i in range(0, n, h * 2):
            for j in range(i, i + h):
                anf[j + h] ^= anf[j]
        h *= 2
    return anf

def calculate_ad(sbox):
    """Menghitung Algebraic Degree (AD)."""
    components = get_bit_components(sbox)
    max_degree = 0
    
    for f in components:
        anf = algebraic_normal_form(f)
        curr_deg = 0
        for i in range(256):
            if anf[i] == 1:
                weight = bin(i).count('1')
                if weight > curr_deg:
                    curr_deg = weight
        if curr_deg > max_degree:
            max_degree = curr_deg
            
    return max_degree

def calculate_ci(sbox):
    """Menghitung Correlation Immunity (CI)."""
    components = get_bit_components(sbox)
    min_ci = 8
    
    for f in components:
        f_signed = np.where(f == 0, 1, -1)
        spectrum = walsh_hadamard_transform(f_signed)
        
        lowest_weight_nonzero = 8
        for w in range(1, 256):
            if spectrum[w] != 0:
                hw = bin(w).count('1')
                if hw < lowest_weight_nonzero:
                    lowest_weight_nonzero = hw
        
        f_ci = lowest_weight_nonzero - 1
        if f_ci < min_ci:
            min_ci = f_ci
            
    return max(0, min_ci)

def calculate_to(sbox):
    """
    Menghitung Transparency Order (TO).
    Rumus (via Autocorrelation): TO = max_beta ( n - (Sum_{a!=0} |AC_beta(a)|) / (N*(N-1)) )
    Semakin kecil nilai TO (ideal), semakin tahan terhadap serangan DPA.
    Namun, S-Box AES standar memiliki TO ~7.8 (yang dianggap tinggi/kurang ideal untuk DPA tanpa masking).
    """
    n = 8
    N = 256
    components = get_bit_components(sbox)
    max_val = -100.0

    # Iterasi semua kombinasi linear beta (1..255)
    for beta in range(1, 256):
        # 1. Konstruksi f_beta = beta * S(x)
        f_beta = np.zeros(N, dtype=int)
        for i in range(8):
            if (beta >> i) & 1:
                f_beta ^= components[i]
        
        # 2. Hitung Spektrum Autocorrelation (AC) menggunakan Teorema Konvolusi
        #    AC(a) = IWHT( WHT(f)^2 ) / N
        f_signed = np.where(f_beta == 0, 1, -1)
        wht = walsh_hadamard_transform(f_signed)
        
        # Kuadratkan spektrum WHT (elemen-wise)
        wht_sq = wht ** 2
        
        # Inverse WHT (di GF(2) sama dengan Forward WHT) dibagi N
        ac = walsh_hadamard_transform(wht_sq) // N
        
        # 3. Hitung metrik untuk beta ini
        #    Sum absolute AC untuk a != 0
        sum_abs_ac = np.sum(np.abs(ac[1:]))
        
        #    Normalisasi
        term = sum_abs_ac / (N * (N - 1))
        val = n - term
        
        if val > max_val:
            max_val = val
            
    return max_val

def calculate_sv(nl, sac, bic_nl, bic_sac):
    """
    Menghitung Strength Value (SV) berdasarkan Eq. 20 di paper.
    SV = (120 - NL) + abs(0.5 - SAC) + (120 - BIC_NL) + abs(0.5 - BIC_SAC)
    Semakin dekat ke 0, semakin baik.
    """
    sv = (120 - nl) + abs(0.5 - sac) + (120 - bic_nl) + abs(0.5 - bic_sac)
    return sv
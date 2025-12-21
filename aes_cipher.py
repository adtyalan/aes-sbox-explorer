import sbox_logic

# Konstanta AES (Rcon)
Rcon = [
    0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40,
    0x80, 0x1B, 0x36, 0x6C, 0xD8, 0xAB, 0x4D, 0x9A
]

class ModifiedAES:
    def __init__(self, key, sbox, inv_sbox):
        self.key = key
        self.sbox = sbox
        self.inv_sbox = inv_sbox
        self.Nb = 4
        self.Nk = len(key) // 4
        self.Nr = 10  # Asumsi kunci 128-bit
        self.w = self.key_expansion(key)

    def sub_word(self, word):
        return [self.sbox[b] for b in word]

    def rot_word(self, word):
        return word[1:] + word[:1]

    def key_expansion(self, key):
        w = [0] * (self.Nb * (self.Nr + 1) * 4)
        for i in range(self.Nk):
            w[4*i] = key[4*i]
            w[4*i+1] = key[4*i+1]
            w[4*i+2] = key[4*i+2]
            w[4*i+3] = key[4*i+3]

        for i in range(self.Nk, self.Nb * (self.Nr + 1)):
            temp = w[4*(i-1):4*i]
            if i % self.Nk == 0:
                temp = self.sub_word(self.rot_word(temp))
                temp[0] ^= Rcon[i // self.Nk]
            
            for j in range(4):
                w[4*i+j] = w[4*(i-self.Nk)+j] ^ temp[j]
        return [w[4*i:4*(i+1)] for i in range(len(w)//4)]

    def add_round_key(self, state, round_key):
        for r in range(4):
            for c in range(4):
                state[r][c] ^= round_key[c][r]
        return state

    def sub_bytes(self, state):
        for r in range(4):
            for c in range(4):
                state[r][c] = self.sbox[state[r][c]]
        return state

    def inv_sub_bytes(self, state):
        for r in range(4):
            for c in range(4):
                state[r][c] = self.inv_sbox[state[r][c]]
        return state

    def shift_rows(self, state):
        state[1] = state[1][1:] + state[1][:1]
        state[2] = state[2][2:] + state[2][:2]
        state[3] = state[3][3:] + state[3][:3]
        return state

    def inv_shift_rows(self, state):
        state[1] = state[1][-1:] + state[1][:-1]
        state[2] = state[2][-2:] + state[2][:-2]
        state[3] = state[3][-3:] + state[3][:-3]
        return state

    def gmul(self, a, b):
        p = 0
        for _ in range(8):
            if b & 1: p ^= a
            hi_bit_set = a & 0x80
            a <<= 1
            if hi_bit_set: a ^= 0x1B
            b >>= 1
        return p & 0xFF

    def mix_columns(self, state):
        for c in range(4):
            col = [state[r][c] for r in range(4)]
            state[0][c] = self.gmul(0x02, col[0]) ^ self.gmul(0x03, col[1]) ^ col[2] ^ col[3]
            state[1][c] = col[0] ^ self.gmul(0x02, col[1]) ^ self.gmul(0x03, col[2]) ^ col[3]
            state[2][c] = col[0] ^ col[1] ^ self.gmul(0x02, col[2]) ^ self.gmul(0x03, col[3])
            state[3][c] = self.gmul(0x03, col[0]) ^ col[1] ^ col[2] ^ self.gmul(0x02, col[3])
        return state

    def inv_mix_columns(self, state):
        for c in range(4):
            col = [state[r][c] for r in range(4)]
            state[0][c] = self.gmul(0x0e, col[0]) ^ self.gmul(0x0b, col[1]) ^ self.gmul(0x0d, col[2]) ^ self.gmul(0x09, col[3])
            state[1][c] = self.gmul(0x09, col[0]) ^ self.gmul(0x0e, col[1]) ^ self.gmul(0x0b, col[2]) ^ self.gmul(0x0d, col[3])
            state[2][c] = self.gmul(0x0d, col[0]) ^ self.gmul(0x09, col[1]) ^ self.gmul(0x0e, col[2]) ^ self.gmul(0x0b, col[3])
            state[3][c] = self.gmul(0x0b, col[0]) ^ self.gmul(0x0d, col[1]) ^ self.gmul(0x09, col[2]) ^ self.gmul(0x0e, col[3])
        return state

    def encrypt_block(self, plaintext):
        state = [[plaintext[r + 4*c] for c in range(4)] for r in range(4)]
        self.add_round_key(state, self.w[:4])

        for round in range(1, self.Nr):
            self.sub_bytes(state)
            self.shift_rows(state)
            self.mix_columns(state)
            self.add_round_key(state, self.w[round*4:(round+1)*4])

        self.sub_bytes(state)
        self.shift_rows(state)
        self.add_round_key(state, self.w[self.Nr*4:])

        res = []
        for c in range(4):
            for r in range(4):
                res.append(state[r][c])
        return bytes(res)

    def decrypt_block(self, ciphertext):
        state = [[ciphertext[r + 4*c] for c in range(4)] for r in range(4)]
        self.add_round_key(state, self.w[self.Nr*4:])

        for round in range(self.Nr - 1, 0, -1):
            self.inv_shift_rows(state)
            self.inv_sub_bytes(state)
            self.add_round_key(state, self.w[round*4:(round+1)*4])
            self.inv_mix_columns(state)

        self.inv_shift_rows(state)
        self.inv_sub_bytes(state)
        self.add_round_key(state, self.w[:4])

        res = []
        for c in range(4):
            for r in range(4):
                res.append(state[r][c])
        return bytes(res)

def pad(data):
    padding_len = 16 - (len(data) % 16)
    return data + bytes([padding_len] * padding_len)

def unpad(data):
    padding_len = data[-1]
    return data[:-padding_len]

def encrypt_text(key_bytes, text, sbox, inv_sbox):
    aes = ModifiedAES(key_bytes, sbox, inv_sbox)
    padded_text = pad(text.encode('utf-8'))
    encrypted = b""
    for i in range(0, len(padded_text), 16):
        block = padded_text[i:i+16]
        encrypted += aes.encrypt_block(block)
    return encrypted.hex()

def decrypt_text(key_bytes, hex_text, sbox, inv_sbox):
    aes = ModifiedAES(key_bytes, sbox, inv_sbox)
    encrypted_bytes = bytes.fromhex(hex_text)
    decrypted = b""
    for i in range(0, len(encrypted_bytes), 16):
        block = encrypted_bytes[i:i+16]
        decrypted += aes.decrypt_block(block)
    return unpad(decrypted).decode('utf-8')

def encrypt_data(key_bytes, data_bytes, sbox, inv_sbox):
    """Fungsi generik untuk mengenkripsi raw bytes (untuk gambar/file)."""
    aes = ModifiedAES(key_bytes, sbox, inv_sbox)
    padded_data = pad(data_bytes)
    encrypted = b""
    
    # Proses blok per blok
    for i in range(0, len(padded_data), 16):
        block = padded_data[i:i+16]
        encrypted += aes.encrypt_block(block)
        
    return encrypted

def decrypt_data(key_bytes, data_bytes, sbox, inv_sbox):
    """Fungsi generik untuk mendekripsi raw bytes."""
    aes = ModifiedAES(key_bytes, sbox, inv_sbox)
    decrypted = b""
    
    for i in range(0, len(data_bytes), 16):
        block = data_bytes[i:i+16]
        decrypted += aes.decrypt_block(block)
        
    return unpad(decrypted)
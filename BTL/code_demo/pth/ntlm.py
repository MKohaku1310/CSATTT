import binascii
import struct
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Thuật toán MD4 chuẩn (Pure Python Implementation - đề phòng môi trường tắt MD4 do chuẩn FIPS)
def md4_pure_python(data: bytes) -> str:
    def F(x, y, z): return (x & y) | (~x & z)
    def G(x, y, z): return (x & y) | (x & z) | (y & z)
    def H(x, y, z): return x ^ y ^ z
    def lrot(x, n): return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF

    # Padding
    msg_len = len(data)
    bit_len = msg_len * 8
    data += b'\x80'
    while (len(data) % 64) != 56:
        data += b'\x00'
    data += struct.pack('<Q', bit_len)

    # Initial values
    A, B, C, D = 0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476

    # Rounds
    for i in range(0, len(data), 64):
        X = list(struct.unpack('<16I', data[i:i+64]))
        AA, BB, CC, DD = A, B, C, D

        # Round 1
        s = [3, 7, 11, 19]
        for j in range(16):
            idx = [A, D, C, B][j % 4]
            if j % 4 == 0: A = lrot((A + F(B, C, D) + X[j]) & 0xFFFFFFFF, s[j % 4])
            elif j % 4 == 1: D = lrot((D + F(A, B, C) + X[j]) & 0xFFFFFFFF, s[j % 4])
            elif j % 4 == 2: C = lrot((C + F(D, A, B) + X[j]) & 0xFFFFFFFF, s[j % 4])
            elif j % 4 == 3: B = lrot((B + F(C, D, A) + X[j]) & 0xFFFFFFFF, s[j % 4])

        # Round 2
        s = [3, 5, 9, 13]
        order2 = [0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15]
        for j in range(16):
            k = order2[j]
            if j % 4 == 0: A = lrot((A + G(B, C, D) + X[k] + 0x5A827999) & 0xFFFFFFFF, s[j % 4])
            elif j % 4 == 1: D = lrot((D + G(A, B, C) + X[k] + 0x5A827999) & 0xFFFFFFFF, s[j % 4])
            elif j % 4 == 2: C = lrot((C + G(D, A, B) + X[k] + 0x5A827999) & 0xFFFFFFFF, s[j % 4])
            elif j % 4 == 3: B = lrot((B + G(C, D, A) + X[k] + 0x5A827999) & 0xFFFFFFFF, s[j % 4])

        # Round 3
        s = [3, 9, 11, 15]
        order3 = [0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15]
        for j in range(16):
            k = order3[j]
            if j % 4 == 0: A = lrot((A + H(B, C, D) + X[k] + 0x6ED9EBA1) & 0xFFFFFFFF, s[j % 4])
            elif j % 4 == 1: D = lrot((D + H(A, B, C) + X[k] + 0x6ED9EBA1) & 0xFFFFFFFF, s[j % 4])
            elif j % 4 == 2: C = lrot((C + H(D, A, B) + X[k] + 0x6ED9EBA1) & 0xFFFFFFFF, s[j % 4])
            elif j % 4 == 3: B = lrot((B + H(C, D, A) + X[k] + 0x6ED9EBA1) & 0xFFFFFFFF, s[j % 4])

        A = (A + AA) & 0xFFFFFFFF
        B = (B + BB) & 0xFFFFFFFF
        C = (C + CC) & 0xFFFFFFFF
        D = (D + DD) & 0xFFFFFFFF

    return struct.pack('<4I', A, B, C, D).hex()

def compute_ntlm_hash(password: str) -> str:
    """
    Tính mã băm NTLM:
    1. Encode mật khẩu sang chuẩn UTF-16LE (Little Endian).
    2. Băm chuỗi byte đó bằng giải thuật MD4.
    """
    utf16le_bytes = password.encode('utf-16le')
    try:
        import hashlib
        return hashlib.new('md4', utf16le_bytes).hexdigest()
    except Exception:
        # Fallback pure python
        return md4_pure_python(utf16le_bytes)

def demo_ntlm_hasher():
    print("=" * 60)
    print("  CÔNG CỤ TÍNH TOÁN VÀ PHÂN TÍCH MÃ BĂM NTLM (WINDOWS)")
    print("=" * 60)
    
    # Test vector trong Báo cáo BTL (Hình 39 & Hình 40)
    sample_pass = "12345678"
    sample_hash = compute_ntlm_hash(sample_pass)
    
    print(f"\n[+] Kiểm tra dữ liệu mẫu trong Báo cáo:")
    print(f"    - Password mẫu : '{sample_pass}'")
    print(f"    - NTLM Hash    : {sample_hash}")
    print(f"    - Khớp với Báo cáo (Hình 40): {sample_hash == '259745cb123a52aa2e693aaacca2db52'}")
    
    print("\n" + "-" * 60)
    while True:
        pwd = input("\nNhập mật khẩu cần tính NTLM hash (hoặc gõ 'q' để thoát): ").strip()
        if pwd.lower() == 'q':
            break
        if not pwd:
            continue
            
        h = compute_ntlm_hash(pwd)
        utf16_hex = pwd.encode('utf-16le').hex()
        
        print(f"  [1] Chuỗi gốc         : {pwd}")
        print(f"  [2] Dạng UTF-16LE Hex : {utf16_hex}")
        print(f"  [3] NTLM (MD4 Hash)   : {h}")
        print(f"  [*] Cú pháp Pass-the-Hash cho Impacket:")
        print(f"      impacket-wmiexec -hashes :{h} username@<IP_VICTIM>")

if __name__ == "__main__":
    demo_ntlm_hasher()

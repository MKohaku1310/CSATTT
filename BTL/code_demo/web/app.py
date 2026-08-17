from flask import Flask, render_template, request, jsonify
import hashlib
import time
import secrets
import string
import struct
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__)

# Thuật toán MD4 thuần Python phòng khi hệ điều hành khóa MD4 theo FIPS
def md4_pure_python(data: bytes) -> str:
    def F(x, y, z): return (x & y) | (~x & z)
    def G(x, y, z): return (x & y) | (x & z) | (y & z)
    def H(x, y, z): return x ^ y ^ z
    def lrot(x, n): return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF

    msg_len = len(data)
    bit_len = msg_len * 8
    data += b'\x80'
    while (len(data) % 64) != 56:
        data += b'\x00'
    data += struct.pack('<Q', bit_len)

    A, B, C, D = 0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476

    for i in range(0, len(data), 64):
        X = list(struct.unpack('<16I', data[i:i+64]))
        AA, BB, CC, DD = A, B, C, D

        # Round 1
        s = [3, 7, 11, 19]
        for j in range(16):
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

def compute_ntlm(password: str) -> str:
    raw = password.encode('utf-16le')
    try:
        return hashlib.new('md4', raw).hexdigest()
    except Exception:
        return md4_pure_python(raw)

def get_hash(algo: str, data_bytes: bytes, key: str = "") -> str:
    combined = data_bytes + key.encode('utf-8')
    algo_clean = algo.lower().replace("-", "").replace("_", "")
    
    if algo_clean == "md5":
        return hashlib.md5(combined).hexdigest()
    elif algo_clean == "sha1":
        return hashlib.sha1(combined).hexdigest()
    elif algo_clean == "sha224":
        return hashlib.sha224(combined).hexdigest()
    elif algo_clean == "sha256":
        return hashlib.sha256(combined).hexdigest()
    elif algo_clean == "sha384":
        return hashlib.sha384(combined).hexdigest()
    elif algo_clean == "sha512":
        return hashlib.sha512(combined).hexdigest()
    elif algo_clean in ("sha3256", "sha3_256"):
        return hashlib.sha3_256(combined).hexdigest()
    elif algo_clean in ("sha3512", "sha3_512"):
        return hashlib.sha3_512(combined).hexdigest()
    elif algo_clean == "ntlm":
        pwd = data_bytes.decode('utf-8', errors='ignore')
        return compute_ntlm(pwd)
    else:
        return hashlib.sha512(combined).hexdigest()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/hash', methods=['POST'])
def api_hash():
    data = request.json or {}
    text = data.get('text', '')
    algo = data.get('algo', 'sha512')
    key = data.get('key', '')
    
    hash_val = get_hash(algo, text.encode('utf-8'), key)
    bit_len = len(bytes.fromhex(hash_val)) * 8
    
    return jsonify({
        'status': 'success',
        'algo': algo.upper(),
        'hash': hash_val,
        'bit_length': bit_len,
        'char_length': len(hash_val)
    })

@app.route('/api/hash_all', methods=['POST'])
def api_hash_all():
    data = request.json or {}
    text = data.get('text', '')
    key = data.get('key', '')
    raw = text.encode('utf-8')
    
    algos = [
        {"name": "MD5", "id": "md5", "family": "MD", "bits": 128, "status": "Broken", "block": 512, "security": "Không an toàn (Đã bị phá va chạm)"},
        {"name": "SHA-1", "id": "sha1", "family": "SHA-1", "bits": 160, "status": "Deprecated", "block": 512, "security": "Không khuyến nghị (Google SHAttered 2017)"},
        {"name": "SHA-256", "id": "sha256", "family": "SHA-2", "bits": 256, "status": "Secure", "block": 512, "security": "An toàn cao (Tiêu chuẩn công nghiệp & Bitcoin)"},
        {"name": "SHA-512", "id": "sha512", "family": "SHA-2", "bits": 512, "status": "Optimal", "block": 1024, "security": "Cực kỳ an toàn (Chuẩn BTL đề tài)"},
        {"name": "SHA3-256", "id": "sha3-256", "family": "Keccak (Sponge)", "bits": 256, "status": "Next-Gen", "block": 1088, "security": "Chống Length Extension Attack"},
        {"name": "SHA3-512", "id": "sha3-512", "family": "Keccak (Sponge)", "bits": 512, "status": "Next-Gen", "block": 576, "security": "An toàn tuyệt đối trong cấu trúc Bọt biển"},
        {"name": "NTLM", "id": "ntlm", "family": "Windows Auth", "bits": 128, "status": "Vulnerable", "block": 512, "security": "Dễ bị tấn công Pass-the-Hash (MD4)"}
    ]
    
    results = []
    for a in algos:
        h = get_hash(a['id'], raw, key)
        results.append({
            **a,
            "hash": h,
            "char_len": len(h)
        })
        
    return jsonify({'results': results})

@app.route('/api/avalanche', methods=['POST'])
def api_avalanche():
    data = request.json or {}
    text1 = data.get('text1', 'PTIT - Mat Ma Hoc Co So 2026')
    text2 = data.get('text2', 'PTIT - Mat Ma Hoc Co So 2027')
    algo = data.get('algo', 'sha512')
    
    hash1 = get_hash(algo, text1.encode('utf-8'))
    hash2 = get_hash(algo, text2.encode('utf-8'))
    
    bin1 = bin(int(hash1, 16))[2:].zfill(len(hash1) * 4)
    bin2 = bin(int(hash2, 16))[2:].zfill(len(hash2) * 4)
    
    diff_count = sum(1 for a, b in zip(bin1, bin2) if a != b)
    total_bits = len(bin1)
    diff_percent = (diff_count / total_bits) * 100 if total_bits else 0
    
    return jsonify({
        'hash1': hash1,
        'hash2': hash2,
        'bin1': bin1,
        'bin2': bin2,
        'total_bits': total_bits,
        'diff_bits': diff_count,
        'diff_percentage': round(diff_percent, 2)
    })

@app.route('/api/preimage_attack', methods=['POST'])
def api_preimage():
    data = request.json or {}
    original_text = data.get('text', 'Hello, I am client!')
    key = data.get('key', 'G08L04DEMOSHA')
    prefix_chars = int(data.get('prefix_chars', 4))  # 4 hex chars = 16 bits
    algo = data.get('algo', 'sha512')
    
    real_hash = get_hash(algo, original_text.encode('utf-8'), key)
    target_prefix = real_hash[:prefix_chars]
    
    chars = string.ascii_letters + string.digits
    attempts = 0
    start_time = time.perf_counter()
    fake_text = ""
    fake_hash = ""
    
    max_attempts = 1500000
    while attempts < max_attempts:
        attempts += 1
        candidate = "".join(secrets.choice(chars) for _ in range(8))
        if candidate == original_text:
            continue
        c_hash = get_hash(algo, candidate.encode('utf-8'), key)
        if c_hash.startswith(target_prefix):
            fake_text = candidate
            fake_hash = c_hash
            break
            
    elapsed = time.perf_counter() - start_time
    
    return jsonify({
        'success': bool(fake_text),
        'original_text': original_text,
        'real_hash': real_hash,
        'target_prefix': target_prefix,
        'fake_text': fake_text,
        'fake_hash': fake_hash,
        'attempts': attempts,
        'elapsed_seconds': round(elapsed, 4),
        'hashes_per_sec': int(attempts / elapsed) if elapsed > 0 else 0
    })

@app.route('/api/ntlm', methods=['POST'])
def api_ntlm():
    data = request.json or {}
    password = data.get('password', '12345678')
    utf16le_hex = password.encode('utf-16le').hex()
    ntlm_hash = compute_ntlm(password)
        
    return jsonify({
        'password': password,
        'utf16le_hex': utf16le_hex,
        'ntlm_hash': ntlm_hash
    })

@app.route('/api/benchmark', methods=['POST'])
def api_benchmark():
    data = request.json or {}
    iterations = int(data.get('iterations', 50000))
    sample = b"PTIT Security Cryptography Lab 2026 Test Benchmark Payload"
    
    algorithms = ['md5', 'sha1', 'sha256', 'sha512', 'sha3-256', 'sha3-512']
    benchmark_results = []
    
    for alg in algorithms:
        start = time.perf_counter()
        if alg == 'md5':
            for _ in range(iterations): hashlib.md5(sample).hexdigest()
        elif alg == 'sha1':
            for _ in range(iterations): hashlib.sha1(sample).hexdigest()
        elif alg == 'sha256':
            for _ in range(iterations): hashlib.sha256(sample).hexdigest()
        elif alg == 'sha512':
            for _ in range(iterations): hashlib.sha512(sample).hexdigest()
        elif alg == 'sha3-256':
            for _ in range(iterations): hashlib.sha3_256(sample).hexdigest()
        elif alg == 'sha3-512':
            for _ in range(iterations): hashlib.sha3_512(sample).hexdigest()
            
        elapsed = time.perf_counter() - start
        ops_sec = int(iterations / elapsed) if elapsed > 0 else 0
        benchmark_results.append({
            'algo': alg.upper(),
            'elapsed_ms': round(elapsed * 1000, 2),
            'ops_per_sec': ops_sec,
            'speed_mb_s': round((ops_sec * len(sample)) / (1024 * 1024), 2)
        })
        
    return jsonify({
        'iterations': iterations,
        'results': benchmark_results
    })

if __name__ == '__main__':
    print("Khởi chạy Web Dashboard tại http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)

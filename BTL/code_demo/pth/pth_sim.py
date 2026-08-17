import os
import sys
import secrets
import hmac
import hashlib
import time

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

from ntlm import compute_ntlm_hash

class WindowsVictimServer:
    """Mô phỏng máy chủ xác thực Windows / Domain Controller"""
    def __init__(self, username="victim", password="Password@123"):
        self.username = username
        self.ntlm_hash = compute_ntlm_hash(password)
        self.current_challenge = None
        
    def generate_challenge(self):
        # Server sinh 8-byte ngẫu nhiên làm Challenge
        self.current_challenge = secrets.token_bytes(8)
        return self.current_challenge
        
    def verify_ntlm_response(self, username, client_response, client_challenge=None):
        if username != self.username:
            return False, "User không tồn tại!"
            
        # Mô phỏng tính toán NT Response dựa trên Server Challenge + NTLM Hash
        expected_response = hmac.new(
            bytes.fromhex(self.ntlm_hash),
            self.current_challenge + (client_challenge or b""),
            hashlib.sha256
        ).digest()
        
        if client_response == expected_response:
            return True, "Xác thực THÀNH CÔNG! Đã cấp quyền truy cập hệ thống."
        else:
            return False, "Xác thực THẤT BẠI: Response không hợp lệ!"

def simulate_pth():
    print("=" * 70)
    print("  MÔ PHỎNG CƠ CHẾ XÁC THỰC NTLM VÀ TẤN CÔNG PASS-THE-HASH (PtH)")
    print("=" * 70)
    
    server = WindowsVictimServer(username="victim", password="MySecretPassword123")
    
    print("\n[THÔNG TIN MÁY NẠN NHÂN (VICTIM)]: ")
    print(f"  - Username nạn nhân : victim")
    print(f"  - Password bí mật   : MySecretPassword123 (Chỉ victim biết, server lưu NTLM Hash)")
    print(f"  - NTLM Hash tại SAM : {server.ntlm_hash}")
    
    print("\n" + "=" * 70)
    print("KỊCH BẢN 1: NGƯỜI DÙNG HỢP LỆ ĐĂNG NHẬP BẰNG MẬT KHẨU")
    print("=" * 70)
    time.sleep(1)
    
    print("1. [Client] Gửi yêu cầu đăng nhập: username = 'victim'")
    challenge = server.generate_challenge()
    print(f"2. [Server] Gửi Challenge ngẫu nhiên (8 bytes): {challenge.hex()}")
    
    # Client nhập password, tự động hash thành NTLM rồi mã hóa Challenge
    client_password = "MySecretPassword123"
    client_hash = compute_ntlm_hash(client_password)
    client_resp = hmac.new(bytes.fromhex(client_hash), challenge, hashlib.sha256).digest()
    print(f"3. [Client] Tính Response = HMAC(NTLM_Hash, Challenge) -> {client_resp.hex()[:16]}...")
    print("   [Client] Gửi Response về Server")
    
    success, msg = server.verify_ntlm_response("victim", client_resp)
    print(f"4. [Server] Kết quả kiểm tra: {msg}")
    
    print("\n" + "=" * 70)
    print("KỊCH BẢN 2: HACKER DÙNG PASS-THE-HASH (KHÔNG BIẾT MẬT KHẨU GỐC)")
    print("=" * 70)
    time.sleep(1)
    print("-> Giả sử Hacker đã dump được NTLM Hash từ bộ nhớ LSASS bằng Mimikatz:")
    print(f"   [!] Hacker thu được NTLM Hash: {server.ntlm_hash}")
    print("   [!] Hacker KHÔNG BIẾT mật khẩu 'MySecretPassword123' là gì.")
    
    input("\n[Nhấn Enter để Hacker thực hiện tấn công Pass-the-Hash qua Impacket/WMI]...")
    
    print("\n1. [Hacker] Gửi yêu cầu kết nối WMI/SMB với user = 'victim'")
    new_challenge = server.generate_challenge()
    print(f"2. [Server] Gửi Challenge ngẫu nhiên mới: {new_challenge.hex()}")
    
    # Hacker không cần giải mã password, đưa trực tiếp NTLM Hash vào thuật toán tính Response!
    stolen_hash = server.ntlm_hash
    hacker_resp = hmac.new(bytes.fromhex(stolen_hash), new_challenge, hashlib.sha256).digest()
    print(f"3. [Hacker] Tính Response trực tiếp từ NTLM Hash bị đánh cắp -> {hacker_resp.hex()[:16]}...")
    print("   [Hacker] Gửi Response giả lập về Server (Pass-the-Hash)")
    
    success, msg = server.verify_ntlm_response("victim", hacker_resp)
    print(f"4. [Server] Kết quả kiểm tra: {msg}")
    
    if success:
        print("\n[+] KẾT LUẬN:")
        print("    -> Cuộc tấn công Pass-the-Hash THÀNH CÔNG RỰC RỠ!")
        print("    -> Vì giao thức NTLM chỉ dùng NTLM Hash làm khóa ký Challenge,")
        print("       nên có Hash đồng nghĩa với có Mật khẩu!")
        print("    -> Giải pháp: Vô hiệu hóa NTLM, chuyển sang dùng giao thức Kerberos.")

if __name__ == "__main__":
    simulate_pth()

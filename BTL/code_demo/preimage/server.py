import socket
import hashlib
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def server_victim_program():
    host = "127.0.0.1"
    port = 12002
    key = "G08L04DEMOSHA"
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)
    
    print("Server sẵn sàng!")
    
    while True:
        try:
            conn, addr = server_socket.accept()
            print(f"Kết nối từ: {addr}")
            
            # 1. Nhận tag
            tag = conn.recv(1024).decode('utf-8', errors='ignore').strip()
            conn.send(b"OK")
            
            # 2. Nhận filename
            filename = conn.recv(1024).decode('utf-8', errors='ignore').strip()
            conn.send(b"OK")
            
            # 3. Nhận size
            size_str = conn.recv(1024).decode('utf-8', errors='ignore').strip()
            total_size = int(size_str)
            conn.send(b"OK")
            
            # 4. Nhận data
            received_bytes = 0
            data_chunks = []
            while received_bytes < total_size:
                chunk = conn.recv(min(4096, total_size - received_bytes))
                if not chunk:
                    break
                data_chunks.append(chunk)
                received_bytes += len(chunk)
            data = b"".join(data_chunks)
            conn.send(b"OK")
            
            # 5. Nhận mã băm mà Client/Attacker gửi lên (Mã hash của thông điệp thật)
            hash_client = conn.recv(1024).decode('utf-8', errors='ignore').strip()
            
            # 6. Server tính hash của dữ liệu nhận được (dữ liệu giả mạo)
            calc_hash_full = hashlib.sha512(data + key.encode('utf-8')).hexdigest()
            
            # Server kiểm tra rút gọn 16-bit (4 ký tự hex đầu) để minh họa cơ chế xác thực rút gọn/tiền tố
            calc_hash_16bit = calc_hash_full[:4]
            client_hash_16bit = hash_client[:4]
            
            print(f"Hash client: {hash_client}")
            print(f"Hash server: {calc_hash_full}")
            try:
                print(f"TEXT: {data.decode('utf-8')}")
            except Exception:
                print(f"DATA: {data}")
                
            # So sánh 4 ký tự hex đầu (16-bit)
            if client_hash_16bit == calc_hash_16bit:
                response = "OK - Dữ liệu toàn vẹn!"
                conn.send(response.encode('utf-8'))
            else:
                response = "LỖI - Dữ liệu bị thay đổi!"
                conn.send(response.encode('utf-8'))
                
            conn.close()
        except Exception as e:
            print(f"Lỗi xử lý kết nối: {e}")

if __name__ == "__main__":
    server_victim_program()

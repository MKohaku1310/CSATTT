import socket
import hashlib
import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def server_program():
    host = "127.0.0.1"
    port = 12001
    
    # Khóa bí mật dùng để xác thực toàn vẹn (MAC)
    key = "G08L04DEMOSHA"
    
    # Thư mục lưu file nhận được
    received_dir = os.path.join(os.path.dirname(__file__), "received_files")
    os.makedirs(received_dir, exist_ok=True)
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)
    
    print("Server sẵn sàng!")
    
    while True:
        try:
            conn, addr = server_socket.accept()
            print(f"Kết nối từ: {addr}")
            
            # 1. Nhận tag (TEXT hoặc FILE)
            tag = conn.recv(1024).decode('utf-8', errors='ignore').strip()
            conn.send(b"OK")
            
            # 2. Nhận tên file
            filename = conn.recv(1024).decode('utf-8', errors='ignore').strip()
            conn.send(b"OK")
            
            # 3. Nhận kích thước dữ liệu
            size_str = conn.recv(1024).decode('utf-8', errors='ignore').strip()
            total_size = int(size_str)
            conn.send(b"OK")
            
            # 4. Nhận toàn bộ dữ liệu theo kích thước
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
            
            # 5. Nhận mã băm từ Client
            hash_client = conn.recv(1024).decode('utf-8', errors='ignore').strip()
            
            # 6. Server tự tính toán lại mã băm bằng SHA-512 + Secret Key
            hash_server = hashlib.sha512(data + key.encode('utf-8')).hexdigest()
            
            print(f"Hash client: {hash_client}")
            print(f"Hash server: {hash_server}")
            
            # 7. So sánh tính toàn vẹn
            if hash_client == hash_server:
                if tag == "TEXT":
                    try:
                        print(f"TEXT: {data.decode('utf-8')}")
                    except Exception:
                        print(f"TEXT (raw): {data}")
                else:
                    save_path = os.path.join(received_dir, filename if filename != "none" else "received_file")
                    with open(save_path, "wb") as f:
                        f.write(data)
                    print(f"Đã lưu file toàn vẹn tại: {save_path} ({len(data)} bytes)")
                
                response = "OK - Dữ liệu toàn vẹn!"
                conn.send(response.encode('utf-8'))
            else:
                response = "LỖI - Dữ liệu bị thay đổi!"
                conn.send(response.encode('utf-8'))
            
            conn.close()
        except Exception as e:
            print(f"Lỗi xử lý kết nối: {e}")

if __name__ == "__main__":
    server_program()

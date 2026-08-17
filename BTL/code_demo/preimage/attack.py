import hashlib
import random
import string
import socket
import time
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def gen_collision_program():
    host = "127.0.0.1"
    port = 12002
    key = "G08L04DEMOSHA"
    
    # 1. Nhập thông điệp thật
    msg_input = input("Nhập thông điệp thật: ").strip()
    if not msg_input:
        msg_input = "Hello, I am client!"
        print(f"Sử dụng thông điệp mặc định: {msg_input}")
        
    msg_real = msg_input.encode('utf-8')
    hash_real = hashlib.sha512(msg_real + key.encode('utf-8')).hexdigest()
    
    print("\n--- THÔNG TIN BAN ĐẦU ---")
    print(f"Thông điệp thật    : {msg_real}")
    print(f"Hash thật: {hash_real}\n")
    
    # Tiền tố mục tiêu (16-bit = 4 ký tự hex đầu)
    target_prefix = hash_real[:4]
    
    # 2. Tìm collision (thông điệp giả mạo)
    chars = string.ascii_letters + string.digits
    attempts = 0
    start_time = time.perf_counter()
    
    fake_msg = ""
    fake_hash = ""
    
    while True:
        attempts += 1
        # Sinh chuỗi ngẫu nhiên độ dài 8 ký tự
        candidate = "".join(random.choices(chars, k=8))
        if candidate.encode('utf-8') == msg_real:
            continue
            
        candidate_hash = hashlib.sha512(candidate.encode('utf-8') + key.encode('utf-8')).hexdigest()
        if candidate_hash.startswith(target_prefix):
            fake_msg = candidate
            fake_hash = candidate_hash
            break
            
    elapsed_time = time.perf_counter() - start_time
    
    print("--- COLLISION TÌM ĐƯỢC ---")
    print(f"Thông điệp giả     : {repr(fake_msg)}")
    print(f"Hash giả           :\n{fake_hash}")
    print(f"Số lần thử         : {attempts}")
    print(f"Thời gian          : {elapsed_time:.4f} giây\n")
    
    # 3. Gửi thông điệp giả mạo kèm hash thật đến server nạn nhân
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        
        fake_data = fake_msg.encode('utf-8')
        tag = "TEXT"
        filename = "none"
        
        # Gửi tag
        client_socket.send(tag.encode('utf-8'))
        client_socket.recv(1024)
        
        # Gửi filename
        client_socket.send(filename.encode('utf-8'))
        client_socket.recv(1024)
        
        # Gửi size
        client_socket.send(str(len(fake_data)).encode('utf-8'))
        client_socket.recv(1024)
        
        # Gửi data giả mạo
        client_socket.sendall(fake_data)
        client_socket.recv(1024)
        
        # Gửi hash thật của thông điệp gốc (để lừa server)
        client_socket.send(hash_real.encode('utf-8'))
        
        # Nhận kết quả từ server
        response = client_socket.recv(1024).decode('utf-8')
        
        print("--- KẾT QUẢ TẤN CÔNG ---")
        print(f"Server phản hồi    : {response}")
        client_socket.close()
    except ConnectionRefusedError:
        print("Lỗi: Không thể kết nối tới server nạn nhân (server_victim.py). Hãy chạy server trước!")
    except Exception as e:
        print(f"Lỗi gửi dữ liệu: {e}")

if __name__ == "__main__":
    gen_collision_program()

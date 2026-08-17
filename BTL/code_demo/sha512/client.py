import socket
import hashlib
import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def client_program():
    host = "127.0.0.1"
    port = 12001
    
    # Khóa bí mật mặc định:
    # TH1 (Toàn vẹn): key = "G08L04DEMOSHA"
    # TH2 (Không toàn vẹn / Sai khóa): đổi thành key khác (ví dụ "G08L04DEMOSHA512")
    key = "G08L04DEMOSHA"
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sample_dir = os.path.join(current_dir, "sample_data")
    
    print("Nhập lựa chọn của bạn:")
    print("1.Gửi thông điệp text \n2.Gửi file text \n3.Gửi hình ảnh \n4.Gửi video")
    choice = input("Chọn: ").strip()
    
    tag = "TEXT"
    filename = "none"
    file_data = b""
    
    if choice == "1":
        text = input("Nhập text: ")
        file_data = text.encode('utf-8')
        tag = "TEXT"
        filename = "none"
    elif choice == "2":
        default_file = os.path.join(sample_dir, "text.txt")
        filepath = input(f"Nhập đường dẫn file (mặc định: {default_file}): ").strip()
        if not filepath:
            filepath = default_file
        
        if not os.path.exists(filepath):
            print(f"Lỗi: Không tìm thấy file {filepath}")
            return
        
        with open(filepath, "rb") as f:
            file_data = f.read()
        tag = "FILE"
        filename = os.path.basename(filepath)
    elif choice == "3":
        default_file = os.path.join(sample_dir, "test.png")
        filepath = input(f"Nhập đường dẫn file ảnh (mặc định: {default_file}): ").strip()
        if not filepath:
            filepath = default_file
            
        if not os.path.exists(filepath):
            print(f"Lỗi: Không tìm thấy file {filepath}")
            return
            
        with open(filepath, "rb") as f:
            file_data = f.read()
        tag = "FILE"
        filename = os.path.basename(filepath)
    elif choice == "4":
        default_file = os.path.join(sample_dir, "sample.mp4")
        filepath = input(f"Nhập đường dẫn file video (mặc định: {default_file}): ").strip()
        if not filepath:
            filepath = default_file
            
        if not os.path.exists(filepath):
            print(f"Lỗi: Không tìm thấy file {filepath}")
            return
            
        with open(filepath, "rb") as f:
            file_data = f.read()
        tag = "FILE"
        filename = os.path.basename(filepath)
    else:
        print("Sai lựa chọn")
        return
        
    # Tính mã băm SHA-512 kết hợp Secret Key (HMAC / MAC)
    hashed = hashlib.sha512(file_data + key.encode('utf-8')).hexdigest()
    
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        
        # 1. Gửi tag
        client_socket.send(tag.encode('utf-8'))
        client_socket.recv(1024)
        
        # 2. Gửi filename
        client_socket.send(filename.encode('utf-8'))
        client_socket.recv(1024)
        
        # 3. Gửi size
        client_socket.send(str(len(file_data)).encode('utf-8'))
        client_socket.recv(1024)
        
        # 4. Gửi data
        client_socket.sendall(file_data)
        client_socket.recv(1024)
        
        # 5. Gửi hash
        client_socket.send(hashed.encode('utf-8'))
        
        # 6. Nhận phản hồi từ Server
        response = client_socket.recv(1024).decode('utf-8')
        print(f"Phản hồi từ phía server: {response}")
        
        client_socket.close()
    except ConnectionRefusedError:
        print("Lỗi: Không thể kết nối tới Server. Hãy đảm bảo tcp_server.py đang chạy!")
    except Exception as e:
        print(f"Lỗi kết nối: {e}")

if __name__ == "__main__":
    client_program()

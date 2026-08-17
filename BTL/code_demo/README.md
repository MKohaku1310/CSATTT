## 1. Cấu trúc Thư mục Mã nguồn

```text
code_demo/
├── sha512/                  # [Mục 5.2] Demo kiểm tra tính toàn vẹn Client - Server
│   ├── server.py            # Server nhận dữ liệu, tính lại SHA-512 + Secret Key
│   ├── client.py            # Client gửi text / file kèm mã băm
│   ├── sample_data/         # File mẫu: text.txt, test.png, sample.mp4
│   └── received_files/      # Thư mục lưu file server nhận được
│
├── preimage/                # [Mục 5.3] Demo Tấn công tiền ảnh thứ hai (Second Preimage)
│   ├── server.py            # Server nạn nhân kiểm tra tiền tố băm (16-bit)
│   └── attack.py            # Tool brute-force tìm thông điệp giả mạo có cùng hash
│
├── pth/                     # [Mục 5.4] Minh họa Pass-the-Hash NTLM
│   ├── ntlm.py              # Hàm tính toán NTLM Hash: MD4(UTF-16LE(Password))
│   ├── pth_sim.py           # Mô phỏng quá trình Challenge-Response & PtH bằng Python
│   └── kali_guide.md        # Hướng dẫn chi tiết chạy máy ảo Kali Linux (Impacket)
│
├── web/                     # Giao diện Web trực quan hóa
│   ├── app.py               # Backend Flask
│   └── templates/index.html # Dashboard Dark-mode trực quan hóa toàn bộ
│
├── run.bat                  # Menu điều khiển chạy tất cả các demo
└── README.md                # Tài liệu hướng dẫn & Kịch bản thuyết trình
```

---

## 2. Hướng dẫn Chạy Demo

Chỉ cần chạy file **`run.bat`** để mở menu điều khiển trực quan:
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

## 3. Kịch bản Thuyết trình Demo

### PHẦN 1: MỤC 5.2 - KIỂM TRA TÍNH TOÀN VẸN (SHA-512 + SECRET KEY)

#### Trường hợp 1: Dữ liệu toàn vẹn
1. **Thao tác**:
   - Mở `run.bat`, chọn `1` (Chạy Server). Server in: `Server sẵn sàng!`.
   - Mở `run.bat`, chọn `2` (Chạy Client).
   - Chọn `1` $\rightarrow$ Nhập `Hello, I am client!`.
2. **Thuyết minh**:
   > *"Client và Server dùng chung Secret Key `G08L04DEMOSHA`. Khi Client gửi thông điệp, Client băm thông điệp kết hợp Secret Key bằng SHA-512 để tạo mã MAC. Server nhận dữ liệu và khóa bí mật của Server rồi băm lại. Vì dữ liệu không bị thay đổi và đúng khóa, hai chuỗi hash trùng khớp. Server phản hồi: `OK - Dữ liệu toàn vẹn!`."*
3. **Thử nghiệm gửi file**: Chọn `2` (File text), `3` (Hình ảnh), `4` (Video) để gửi file mẫu. Server nhận và lưu file vào `sha512/received_files/`.

#### Trường hợp 2: Dữ liệu bị thay đổi / Sai khóa
1. **Thao tác**: Sửa biến `key` trong [sha512/client.py](file:///d:/PTIT/IT-VN%20Y3-1/CSATTT/BTL/code_demo/sha512/client.py) thành `"G08L04DEMOSHA512"`. Chạy lại Client gửi tin.
2. **Kết quả**: Hai giá trị hash lệch nhau hoàn toàn $\rightarrow$ Server từ chối và báo `LỖI - Dữ liệu bị thay đổi!`.
3. **Thuyết minh**:
   > *"Nhờ tính chất Tuyết lở (Avalanche Effect), chỉ cần đổi 1 ký tự hoặc sai khóa, giá trị băm tại Server sẽ biến đổi ngẫu nhiên hoàn toàn. Server phát hiện ngay sự sai lệch."*

---

### PHẦN 2: MỤC 5.3 - TẤN CÔNG TIỀN ẢNH THỨ HAI (SECOND PREIMAGE ATTACK)

1. **Ý tưởng**:
   - Cho trước thông điệp thật $m_1$, tìm thông điệp giả $m_2 \neq m_1$ sao cho $H(m_2) = H(m_1)$.
   - Để demo trực tiếp trong vài giây, chương trình cài đặt so sánh **16-bit đầu tiên (4 ký tự hex đầu)** ($2^{16} = 65,536$ khả năng).
2. **Thao tác**:
   - Chạy Server: chọn `3` trong `run.bat` ([preimage/server.py](file:///d:/PTIT/IT-VN%20Y3-1/CSATTT/BTL/code_demo/preimage/server.py)).
   - Chạy Attack: chọn `4` trong `run.bat` ([preimage/attack.py](file:///d:/PTIT/IT-VN%20Y3-1/CSATTT/BTL/code_demo/preimage/attack.py)).
   - Nhập chuỗi thật: `Hello, I am client!`.
3. **Kết quả**:
   - Tool tìm ra thông điệp giả (ví dụ `KuXJV018`) có 4 ký tự đầu của hash trùng với hash của thông điệp thật trong vòng ~0.2 giây.
   - Gửi dữ liệu giả mạo kèm hash thật lên Server $\rightarrow$ Server chỉ kiểm tra tiền tố nên bị đánh lừa: **`OK - Dữ liệu toàn vẹn!`**.

---

### PHẦN 3: MỤC 5.4 - MINH HỌA PASS-THE-HASH (PtH) NTLM

Nhóm chuẩn bị 2 phương án demo linh hoạt:

#### 🔹 Phương án A: Thực chiến bằng Kali Linux (WSL2) $\leftrightarrow$ Windows (Chân thực 100%)
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

#### 🔹 Phương án B: Mô phỏng bằng Python / Web Visualizer
- Chọn `5` trong `run.bat` ([pth/pth_sim.py](file:///d:/PTIT/IT-VN%20Y3-1/CSATTT/BTL/code_demo/pth/pth_sim.py)):
  - Xem mô phỏng quá trình Server gửi Challenge và Client/Attacker ký HMAC bằng NTLM Hash.
  - Phân tích toán học vì sao NTLM Hash $MD4(UTF\text{-}16LE(Password))$ bị dùng để đăng nhập mà không cần password gốc.
- Chi tiết hướng dẫn xem thêm tại [pth/kali_guide.md](file:///d:/PTIT/IT-VN%20Y3-1/CSATTT/BTL/code_demo/pth/kali_guide.md).

---

### PHẦN 4: MỤC 5.5 - WEB DASHBOARD TRỰC QUAN

- **Thao tác**: Chọn `6` trong `run.bat` $\rightarrow$ Tự động mở trình duyệt `http://127.0.0.1:5000`.
- **Nội dung trình diễn**:
  1. *Tính toàn vẹn*: Thử đổi ký tự để xem cảnh báo trực quan.
  2. *Hiệu ứng Tuyết lở (Avalanche)*: So sánh `PTIT 2026` vs `PTIT 2027`, xem tỉ lệ bit đổi (~51%).
  3. *Tấn công tiền ảnh*: Chạy vét cạn đồ họa thời gian thực.
  4. *NTLM Hasher*: Chuyển đổi chuỗi sang NTLM hash.

---

## 4. Bộ 10 Câu hỏi Phản biện & Đáp án

### Câu 1: Tại sao phải thêm Secret Key vào dữ liệu trước khi băm?
- **Đáp án**: Nếu chỉ gửi $M$ và $H(M)$ (MDC), kẻ tấn công đứng giữa (MitM) có thể sửa $M$ thành $M'$ rồi tự tính lại $H(M')$ gửi cho Server. Thêm Secret Key $K$ ($H(M || K)$ - MAC) đảm bảo kẻ tấn công không biết $K$ nên không thể tạo ra mã băm giả mạo hợp lệ.

### Câu 2: Phân biệt 3 tính chất an toàn của hàm băm?
1. **Kháng tiền ảnh (Preimage Resistance)**: Cho trước hash $h$, khó tìm $m$ sao cho $H(m) = h$. Độ phức tạp: $\mathcal{O}(2^n)$.
2. **Kháng tiền ảnh thứ hai (Second Preimage Resistance)**: Cho trước $m_1$, khó tìm $m_2 \neq m_1$ sao cho $H(m_2) = H(m_1)$. Độ phức tạp: $\mathcal{O}(2^n)$.
3. **Kháng va chạm (Collision Resistance)**: Khó tìm bất kỳ cặp $(m_1, m_2)$ nào sao cho $H(m_1) = H(m_2)$. Độ phức tạp: $\mathcal{O}(2^{n/2})$ (theo Nghịch lý ngày sinh nhật).

### Câu 3: Tại sao MD5/SHA-1 không còn an toàn, còn SHA-2 vẫn an toàn?
- MD5 (128-bit) và SHA-1 (160-bit) đã bị tấn công va chạm thực tế (như dự án SHAttered của Google năm 2017 tạo ra 2 PDF khác nhau có cùng SHA-1). SHA-2 (SHA-256, SHA-512) có không gian băm lớn hơn rất nhiều, lịch trình thông điệp phức tạp và chưa có kỹ thuật nào nhanh hơn vét cạn.

### Câu 4: Cấu trúc Sponge trong SHA-3 có ưu điểm gì so với Merkle-Damgård?
- Merkle-Damgård dễ bị tấn công mở rộng độ dài (**Length Extension Attack**). SHA-3 (Keccak) chia trạng thái nội bộ thành *Rate* và *Capacity*, trong đó *Capacity* luôn được giấu kín trong hàm hoán vị, giúp SHA-3 miễn nhiễm hoàn toàn với Length Extension Attack.

### Câu 5: Hiệu ứng Tuyết lở (Avalanche Effect) là gì?
- Khi thay đổi chỉ **1 bit** đầu vào, đầu ra hàm băm sẽ thay đổi ngẫu nhiên khoảng **50% số bit**. Điều này ngăn chặn việc đoán cấu trúc hay tìm mối liên hệ toán học giữa đầu vào và đầu ra.

### Câu 6: Tấn công Length Extension Attack là gì?
- Với hàm băm Merkle-Damgård dạng $H(K || M)$, nếu kẻ tấn công biết độ dài $K$, nội dung $M$ và giá trị $H(K || M)$, kẻ tấn công có thể tính được $H(K || M || padding || data\_mới)$ mà không cần biết $K$. Khắc phục bằng cách dùng chuẩn **HMAC** hoặc chuyển sang **SHA-3**.

### Câu 7: Tại sao giao thức NTLM trên Windows lại bị Pass-the-Hash?
- NTLM Hash là $MD4(UTF\text{-}16LE(Password))$ được lưu tĩnh trong SAM/LSASS mà không có Salt động. Giao thức chỉ yêu cầu dùng chính NTLM Hash này để mã hóa Challenge nên kẻ tấn công trộm được Hash có thể đăng nhập mà không cần password gốc.

### Câu 8: Cách ngăn chặn Pass-the-Hash?
- Vô hiệu hóa NTLM, bắt buộc dùng **Kerberos**.
- Bật **Credential Guard**, **LAPS (Local Administrator Password Solution)** và kích hoạt bảo vệ tiến trình LSASS (`RunAsPPL`).

### Câu 9: Máy tính lượng tử (thuật toán Grover) ảnh hưởng thế nào đến hàm băm?
- Thuật toán Grover giảm độ an toàn tìm tiền ảnh từ $\mathcal{O}(2^n)$ xuống $\mathcal{O}(2^{n/2})$. SHA-256 sẽ còn tương đương độ an toàn 128-bit. Giải pháp hậu lượng tử là nâng kích thước lên gấp đôi: dùng **SHA-384** hoặc **SHA-512**.

### Câu 10: Phân biệt Hàm băm và Mã hóa đối xứng?
- **Hàm băm**: Là hàm một chiều (One-way), nén kích thước bất kỳ thành kích thước cố định, **không thể giải mã ngược lại**. Mục đích: Toàn vẹn (Integrity) và Xác thực (Authentication).
- **Mã hóa đối xứng (AES, DES)**: Là hàm hai chiều (Two-way) dùng chung một khóa để mã hóa và giải mã. Mục đích: Tính bí mật (Confidentiality).

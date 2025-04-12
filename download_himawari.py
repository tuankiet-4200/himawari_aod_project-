import os
import time
from ftplib import FTP
import subprocess
from datetime import datetime, timedelta

FTP_HOST = "ftp.ptree.jaxa.jp"
FTP_USER = "tuankiet24022020_gmail.com"
FTP_PASS = "SP+wari8"
BASE_DIR = "/pub/himawari/L2/ARP/031"

# Cấu hình thư mục local
LOCAL_BASE = "C:/Users/Admin/himawari_project_v2/himawari_data_v2"
PROCESS_SCRIPT = "C:/Users/Admin/himawari_project_v2/process_aod_data.py"
LOG_FILE = "C:/Users/Admin/himawari_project_v2/downloaded_files.log"

# Thời gian bắt đầu
start_time = datetime(2025, 4, 4, 0, 0)

# Đọc log file
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r") as f:
        downloaded = set(line.strip() for line in f)
else:
    downloaded = set()

def save_log(filename):
    with open(LOG_FILE, "a") as f:
        f.write(filename + "\n")
    downloaded.add(filename)

def download_and_process(ftp, remote_path, local_path):
    os.makedirs(local_path, exist_ok=True)
    try:
        ftp.cwd(remote_path)
        files = ftp.nlst()
        if not files:
            return False

        for file in files:
            if file in downloaded:
                continue

            local_file = os.path.join(local_path, file)
            with open(local_file, "wb") as f:
                ftp.retrbinary(f"RETR " + file, f.write)
            print(f"✅ Đã tải: {file}")

            # Gọi xử lý file .nc
            subprocess.run(["python", PROCESS_SCRIPT, local_file])
            save_log(file)

        return True

    except Exception as e:
        print(f"⛔ Không truy cập được {remote_path}: {e}")
        return False

def main():
    global start_time
    while True:
        try:
            ftp = FTP(FTP_HOST)
            ftp.login(FTP_USER, FTP_PASS)
            print(f"🔄 Đang kiểm tra dữ liệu tại {start_time.strftime('%Y-%m-%d %H:%M')}...")

            ymd = start_time.strftime("%Y%m")
            dd = start_time.strftime("%d")
            hh = start_time.strftime("%H")
            remote_path = f"{BASE_DIR}/{ymd}/{dd}/{hh}/"
            local_path = os.path.join(LOCAL_BASE, ymd, dd, hh)

            success = download_and_process(ftp, remote_path, local_path)
            ftp.quit()

            # Nếu có file → sang giờ tiếp theo, nếu không → đợi 10 phút
            if success:
                print(f"👉 Xử lý xong {remote_path}\n")
                start_time += timedelta(hours=1)
            else:
                print(f"⏳ Không có dữ liệu, thử lại sau 10 phút...\n")
                time.sleep(600)  # 10 phút

        except Exception as e:
            print(f"⚠️ Lỗi khi kết nối FTP: {e}")
            time.sleep(600)

if __name__ == "__main__":
    main()

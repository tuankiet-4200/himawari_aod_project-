import pandas as pd
import os

# Danh sách các file cần xử lý
files = [
    "all_station_aod05.csv",
    "all_station_aod07.csv", 
    "all_station_aod08.csv",
    "all_station_aod1.csv",
    "all_station_aod12.csv",
    "all_station_aod15.csv"
]

# Xử lý từng file
for file_name in files:
    if os.path.exists(file_name):
        print(f"Đang xử lý file: {file_name}")
        
        # Đọc file CSV
        df = pd.read_csv(file_name)
        
        # Xoá các cột toàn bộ là NaN
        df_cleaned = df.dropna(axis=1, how='all')
        
        # Ghi lại vào chính file đó
        df_cleaned.to_csv(file_name, index=False)
        
        print(f"✅ Đã xử lý xong: {file_name}")
    else:
        print(f"❌ Không tìm thấy file: {file_name}")

print("\n🎉 Hoàn thành xử lý tất cả các file!")
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
import seaborn as sns
import re
import unicodedata
from matplotlib.dates import DateFormatter

# Hàm chuyển tên trạm thành tên file an toàn
def safe_filename(s):
    s = unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode('utf-8')
    s = re.sub(r'[^a-zA-Z0-9]+', '_', s)
    return s.strip('_').lower()

# Danh sách các file AOD cần xử lý
aod_files = [
    "all_station_aod05.csv",
    "all_station_aod07.csv", 
    "all_station_aod08.csv",
    "all_station_aod1.csv",
    "all_station_aod12.csv",
    "all_station_aod15.csv"
]

# Tạo thư mục gốc để lưu biểu đồ
base_dir = 'aod_station'
os.makedirs(base_dir, exist_ok=True)

for aod_file in aod_files:
    if not os.path.exists(aod_file):
        print(f"❌ Không tìm thấy file: {aod_file}")
        continue
    print(f"Đang xử lý file: {aod_file}")
    
    # Đọc dữ liệu
    df = pd.read_csv(aod_file)
    aod_level = aod_file.replace('all_station_aod', '').replace('.csv', '')
    
    # Lấy tất cả các cột bắt đầu bằng AOT_
    aot_columns = [col for col in df.columns if col.startswith('AOT_')]
    
    # Loại bỏ các cột không đúng format timestamp
    valid_aot_columns = []
    for col in aot_columns:
        try:
            datetime.strptime(col.replace('AOT_', ''), '%Y%m%d_%H%M')
            valid_aot_columns.append(col)
        except Exception:
            print(f"⚠️  Bỏ qua cột không đúng format: {col}")
    
    if not valid_aot_columns:
        print(f"❌ Không có cột AOT hợp lệ trong file {aod_file}")
        continue
    
    # Tạo DataFrame với thời gian
    df_melted = pd.melt(df, 
                        id_vars=['station_id', 'station_name', 'Latitude', 'Longitude'],
                        value_vars=valid_aot_columns,
                        var_name='timestamp',
                        value_name='aod')
    
    df_melted['timestamp'] = df_melted['timestamp'].str.replace('AOT_', '')
    df_melted['datetime'] = pd.to_datetime(df_melted['timestamp'], format='%Y%m%d_%H%M')
    df_melted['month'] = df_melted['datetime'].dt.strftime('%Y%m')
    
    # Sau khi melt:
    df_melted['aod'] = pd.to_numeric(df_melted['aod'], errors='coerce')
    df_melted = df_melted[df_melted['aod'].notnull()]
    df_melted = df_melted[df_melted['aod'] > 0]
    
    # Debug: In số dòng hợp lệ cho từng trạm
    for month, month_data in df_melted.groupby('month'):
        month_dir = os.path.join(base_dir, f'aod_station_{month}')
        level_dir = os.path.join(month_dir, f'aod_station_{month}_{aod_level}')
        os.makedirs(level_dir, exist_ok=True)
        for station_id, station_data in month_data.groupby('station_id'):
            station_name = station_data['station_name'].iloc[0]
            print(f"Trạm {station_id} ({station_name}) tháng {month} có {len(station_data)} dòng dữ liệu hợp lệ")
            if len(station_data) == 0:
                continue

            # Tạo nhãn giờ
            station_data = station_data.copy()
            station_data['hour_label'] = station_data['datetime'].dt.strftime('%m-%d %H')
            station_data['date'] = station_data['datetime'].dt.date

            # Tính trung bình AOD theo từng giờ
            hourly_aod = station_data.groupby(['date', 'hour_label'])['aod'].mean().reset_index()

            # Chèn NaN giữa các ngày
            hourly_aod_with_gaps = []
            prev_date = None
            for _, row in hourly_aod.iterrows():
                if prev_date is not None and row['date'] != prev_date:
                    # Chèn 2 dòng NaN để tạo 2 ô trống
                    hourly_aod_with_gaps.append({'hour_label': '', 'aod': float('nan')})
                    hourly_aod_with_gaps.append({'hour_label': '', 'aod': float('nan')})
                hourly_aod_with_gaps.append({'hour_label': row['hour_label'], 'aod': row['aod']})
                prev_date = row['date']

            hourly_aod_with_gaps = pd.DataFrame(hourly_aod_with_gaps)

            plt.figure(figsize=(24, 8))
            sns.set_style("whitegrid")
            plt.plot(hourly_aod_with_gaps['hour_label'], hourly_aod_with_gaps['aod'],
                     marker='o', linestyle='-', linewidth=1, markersize=4)

            plt.title(f'AOD (uncertainty {aod_level}) tại trạm {station_name} - Tháng {month[:4]}/{month[4:]}')
            plt.xlabel('Thời gian (giờ)')
            plt.ylabel('AOD')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.grid(True, axis='both', linestyle='--', alpha=0.5)

            output_file = os.path.join(level_dir, f'station_{station_id}_{safe_filename(station_name)}.png')
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()
        print(f"  ✅ Đã xử lý tháng {month} với mức uncertainty {aod_level}")

print("✅ Đã hoàn thành vẽ biểu đồ AOD cho tất cả các trạm và mức uncertainty!") 
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
import seaborn as sns
import matplotlib.dates as mdates # Import mdates for date formatting

# Đọc dữ liệu
df = pd.read_csv('all_station_aod_cleaned.csv')
print("DataFrame gốc sau khi đọc CSV:")
print(df.head())
print(f"Số dòng trong DataFrame gốc: {len(df)}")

# Tạo thư mục gốc để lưu biểu đồ
base_dir = 'aod_station'
os.makedirs(base_dir, exist_ok=True)

# Lấy danh sách các cột AOT (bỏ qua các cột khác)
aot_columns = [col for col in df.columns if col.startswith('AOT_')]

# Tạo DataFrame với thời gian
df_melted = pd.melt(df, 
                    id_vars=['station_id', 'station_name', 'Latitude', 'Longitude'],
                    value_vars=aot_columns,
                    var_name='timestamp',
                    value_name='aod')
print("\nDataFrame sau khi melt:")
print(df_melted.head())
print(f"Số dòng trong DataFrame sau khi melt: {len(df_melted)}")

# Chuyển đổi timestamp
df_melted['timestamp'] = df_melted['timestamp'].str.replace('AOT_', '')
# Thêm error='coerce' để các timestamp không hợp lệ sẽ thành NaT (Not a Time)
df_melted['datetime'] = pd.to_datetime(df_melted['timestamp'], format='%Y%m%d_%H%M', errors='coerce')
df_melted['month'] = df_melted['datetime'].dt.strftime('%Y%m')
print("\nDataFrame sau khi chuyển đổi timestamp và thêm cột tháng:")
print(df_melted.head())
print(f"Số dòng trong DataFrame sau khi xử lý timestamp: {len(df_melted)}")
# Kiểm tra các dòng có timestamp không hợp lệ
invalid_timestamps = df_melted[df_melted['datetime'].isna()]
if not invalid_timestamps.empty:
    print(f"\n⚠️ Cảnh báo: Có {len(invalid_timestamps)} dòng có timestamp không hợp lệ:")
    print(invalid_timestamps.head())


# Lọc bỏ các giá trị AOD <= 0 hoặc là NaN
# Chuyển cột 'aod' sang dạng số, các giá trị không phải số sẽ thành NaN
df_melted['aod'] = pd.to_numeric(df_melted['aod'], errors='coerce')
df_melted_filtered = df_melted[(df_melted['aod'] > 0) & (df_melted['datetime'].notna())].copy() # Lọc AOD > 0 và datetime hợp lệ
print("\nDataFrame sau khi lọc AOD > 0 và datetime hợp lệ:")
print(df_melted_filtered.head())
print(f"Số dòng trong DataFrame sau khi lọc: {len(df_melted_filtered)}")

# Kiểm tra dữ liệu cho trạm Long An trong tháng 3/2025 sau khi lọc
long_an_march_data = df_melted_filtered[(df_melted_filtered['station_name'] == 'Long An') & (df_melted_filtered['month'] == '202503')]
print("\nDữ liệu Long An (station_name == 'Long An') trong tháng 202503 sau khi lọc:")
print(long_an_march_data)
print(f"Số dòng dữ liệu Long An tháng 202503 sau khi lọc: {len(long_an_march_data)}")


# Vẽ biểu đồ cho từng tháng và từng trạm (sử dụng df_melted_filtered)
for month, month_data in df_melted_filtered.groupby('month'):
    # Tạo thư mục cho tháng
    month_dir = os.path.join(base_dir, month)
    os.makedirs(month_dir, exist_ok=True)
    
    # Vẽ biểu đồ cho từng trạm trong tháng
    for station_id, station_data in month_data.groupby('station_id'):
        station_name = station_data['station_name'].iloc[0]
        
        print(f"\nĐang vẽ biểu đồ cho trạm {station_name} (ID: {station_id}) trong tháng {month}")
        # Kiểm tra số điểm dữ liệu trước khi vẽ
        if len(station_data) == 0:
            print(f"Không có dữ liệu AOD > 0 cho trạm {station_name} trong tháng {month} sau khi lọc. Bỏ qua vẽ biểu đồ.")
            # Tạo file 0KB để đánh dấu trạm này không có dữ liệu đủ điều kiện vẽ trong tháng này
            open(os.path.join(month_dir, f'station_{station_id}_{station_name.replace("/", "_").replace(":", "_")}.png'), 'a').close()
            continue

        plt.figure(figsize=(15, 6))
        sns.set_style("whitegrid")
        
        # Vẽ biểu đồ sử dụng chỉ mục cho trục X
        plt.plot(range(len(station_data)), station_data['aod'], 
                marker='o', linestyle='-', linewidth=1, markersize=4)
        
        # Cấu hình trục X chỉ hiển thị các mốc thời gian có dữ liệu
        plt.xticks(range(len(station_data)), 
                   station_data['datetime'].dt.strftime('%m-%d %H:%M'), # Format datetime objects to strings (tháng-ngày giờ:phút)
                   rotation=45, ha='right', fontsize=2) # Xoay nhãn, căn phải, và giảm kích thước font
        
        # Thêm lưới dọc tại các điểm dữ liệu
        plt.grid(axis='x', linestyle='--', alpha=0.6)

        # Cấu hình biểu đồ
        plt.title(f'AOD tại trạm {station_name} - Tháng {month[:4]}/{month[4:]}')
        plt.xlabel('Thời gian')
        plt.ylabel('AOD')
        
        plt.tight_layout()
        
        # Lưu biểu đồ
        output_file = os.path.join(month_dir, f'station_{station_id}_{station_name.replace("/", "_").replace(":", "_")}.png') # Thay thế ký tự đặc biệt trong tên file
        try:
            # Tăng DPI để tăng độ phân giải
            plt.savefig(output_file, dpi=600, bbox_inches='tight')
            print(f"✅ Đã lưu biểu đồ: {output_file}")
        except Exception as e:
            print(f"❌ Lỗi khi lưu biểu đồ {output_file}: {e}")
            
        plt.close()

print("\n✅ Đã hoàn thành quá trình vẽ biểu đồ AOD.") 
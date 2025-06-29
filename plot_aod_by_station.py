import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
import seaborn as sns

# Đọc dữ liệu
df = pd.read_csv('all_station_aod_cleaned.csv')

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

# Chuyển đổi timestamp
df_melted['timestamp'] = df_melted['timestamp'].str.replace('AOT_', '')
df_melted['datetime'] = pd.to_datetime(df_melted['timestamp'], format='%Y%m%d_%H%M')
df_melted['month'] = df_melted['datetime'].dt.strftime('%Y%m')

# Lọc bỏ các giá trị AOD <= 0
df_melted = df_melted[df_melted['aod'] > 0]

# Vẽ biểu đồ cho từng tháng và từng trạm
for month, month_data in df_melted.groupby('month'):
    # Tạo thư mục cho tháng
    month_dir = os.path.join(base_dir, month)
    os.makedirs(month_dir, exist_ok=True)
    
    # Vẽ biểu đồ cho từng trạm trong tháng
    for station_id, station_data in month_data.groupby('station_id'):
        station_name = station_data['station_name'].iloc[0]
        
        plt.figure(figsize=(15, 6))
        sns.set_style("whitegrid")
        
        # Vẽ biểu đồ
        plt.plot(station_data['datetime'], station_data['aod'], 
                marker='o', linestyle='-', linewidth=1, markersize=4)
        
        # Cấu hình biểu đồ
        plt.title(f'AOD tại trạm {station_name} - Tháng {month[:4]}/{month[4:]}')
        plt.xlabel('Thời gian')
        plt.ylabel('AOD')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Lưu biểu đồ
        output_file = os.path.join(month_dir, f'station_{station_id}_{station_name}.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

print("✅ Đã hoàn thành vẽ biểu đồ AOD cho tất cả các trạm!") 
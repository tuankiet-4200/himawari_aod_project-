import sys
import os
import pandas as pd
import rasterio
import numpy as np

if len(sys.argv) < 2:
    print("⚠️ Thiếu đường dẫn file GeoTIFF")
    sys.exit(1)

aod_file = sys.argv[1]
stations_file = "C:/Users/Admin/Desktop/himawari_project_v2/stations.csv"
output_csv = "C:/Users/Admin/Desktop/himawari_project_v2/all_station_aod.csv"

# Lấy timestamp từ tên file
filename = os.path.basename(aod_file)
parts = filename.split("_")
timestamp = parts[4] + "_" + parts[5]
aot_col_name = f"AOT_{timestamp}"

# Đọc danh sách trạm
stations = pd.read_csv(stations_file)
stations = stations.rename(columns={"Name": "station_name"})

if "station_id" not in stations.columns:
    stations["station_id"] = range(len(stations))

# Đọc ảnh AOT và uncertainty
with rasterio.open(aod_file) as src:
    aot_values = []
    
    for _, row in stations.iterrows():
        lon, lat = row["Longitude"], row["Latitude"]
        try:
            rowcol = src.index(lon, lat)
            aot_value = src.read(1)[rowcol[0], rowcol[1]]
            uncertainty_value = src.read(2)[rowcol[0], rowcol[1]]
            
            # Chỉ lấy AOT nếu uncertainty < 1
            if np.isnan(aot_value) or np.isnan(uncertainty_value) or uncertainty_value >= 1:
                aot_value = None
                
        except Exception as e:
            aot_value = None
            
        aot_values.append(aot_value)

# Thêm cột AOT vào DataFrame
stations[aot_col_name] = aot_values

# Ghi hoặc cập nhật file tổng
if os.path.exists(output_csv):
    df_old = pd.read_csv(output_csv)
    df_merged = pd.merge(df_old, 
                        stations[["station_id", aot_col_name]], 
                        on="station_id", 
                        how="left")
else:
    df_merged = stations[["station_id", "station_name", "Latitude", "Longitude", 
                         aot_col_name]]

df_merged.to_csv(output_csv, index=False)
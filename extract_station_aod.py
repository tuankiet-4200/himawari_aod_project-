import sys
import os
import pandas as pd
import rasterio

if len(sys.argv) < 2:
    print("⚠️ Thiếu đường dẫn file GeoTIFF")
    sys.exit(1)

aod_file = sys.argv[1]
stations_file = "C:/Users/Admin/himawari_project_v2/stations.csv"
output_csv = "C:/Users/Admin/himawari_project_v2/all_station_aod.csv"  # File tổng

# Lấy timestamp từ tên file GeoTIFF
filename = os.path.basename(aod_file)
# Ví dụ: aod_vietnam_NC_H09_20250404_0010_L2ARP031_FLDK.02401_02401.tif
parts = filename.split("_")
timestamp = parts[4] + "_" + parts[5]  # "20250404_0010"
aod_col_name = f"AOD_{timestamp}"

# Đọc danh sách trạm
stations = pd.read_csv(stations_file)
stations = stations.rename(columns={"Name": "station_name"})  # Đổi tên cột nếu cần

# Tạo cột station_id nếu chưa có
if "station_id" not in stations.columns:
    stations["station_id"] = range(len(stations))

# Đọc ảnh AOD
with rasterio.open(aod_file) as src:
    aod_values = []
    for _, row in stations.iterrows():
        lon, lat = row["Longitude"], row["Latitude"]
        try:
            rowcol = src.index(lon, lat)
            value = src.read(1)[rowcol[0], rowcol[1]]
        except:
            value = None
        aod_values.append(value)

# Ghép vào DataFrame kết quả
stations[aod_col_name] = aod_values

# Ghi hoặc cập nhật file tổng
if os.path.exists(output_csv):
    df_old = pd.read_csv(output_csv)
    df_merged = pd.merge(df_old, stations[["station_id", aod_col_name]], on="station_id", how="left")
else:
    df_merged = stations[["station_id", "station_name", "Latitude", "Longitude", aod_col_name]]

df_merged.to_csv(output_csv, index=False)
print(f"✅ Đã cập nhật dữ liệu vào: {output_csv}")

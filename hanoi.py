import os
import geopandas as gpd

# Tạo thư mục con 'hanoi' trong thư mục hiện tại
output_dir = "./hanoi"
os.makedirs(output_dir, exist_ok=True)

# Đọc file shapefile từ thư mục đã tải về
shapefile_path = "C:/Users/Admin/himawari_project_v2/VNM_adm/VNM_adm1.shp"
gdf = gpd.read_file(shapefile_path)

print("Các cột có trong file shapefile:", gdf.columns)

for col in gdf.columns:
    print(f"Giá trị trong cột '{col}': {gdf[col].unique()[:10]}")

hanoi_data = gdf[gdf["NAME_1"] == "Hà Nội"]

if hanoi_data.empty:
    print("Không tìm thấy Hà Nội trong dữ liệu.")
else:
    print("Tìm thấy dữ liệu Hà Nội:")
    print(hanoi_data)

# Xuất shapefile Hà Nội vào thư mục 'hanoi'
if not hanoi_data.empty:
    output_path = os.path.join(output_dir, "hanoi_shapefile.shp")
    hanoi_data.to_file(output_path)
    print(f"Đã xuất dữ liệu Hà Nội ra: {output_path}")

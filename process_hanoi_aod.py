import os
import rasterio
from rasterio.mask import mask
import geopandas as gpd
import numpy as np

def crop_hanoi_aod(input_tif_path, hanoi_shapefile_path, output_tif_path):
    # Đọc shapefile Hà Nội
    hanoi_gdf = gpd.read_file(hanoi_shapefile_path)

    # Đọc raster AOD Vietnam
    with rasterio.open(input_tif_path) as src:
        # Đảm bảo hệ tọa độ khớp giữa shapefile và raster
        hanoi_gdf = hanoi_gdf.to_crs(src.crs)
        # Cắt ảnh theo shapefile Hà Nội
        out_image, out_transform = mask(src, hanoi_gdf.geometry, crop=True)
        out_meta = src.meta.copy()
        out_meta.update({
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform
        })

    # Ghi ảnh AOD sau khi cắt ra file mới
    with rasterio.open(output_tif_path, "w", **out_meta) as dest:
        dest.write(out_image)

    # Tính trung bình và lớn nhất AOD (loại bỏ giá trị <= 0)
    aod_data = out_image[0]
    valid_data = aod_data[aod_data > 0]

    mean_aod = np.mean(valid_data) if valid_data.size > 0 else np.nan
    max_aod = np.max(valid_data) if valid_data.size > 0 else np.nan
    min_aod = np.min(valid_data) if valid_data.size > 0 else np.nan

    print(f"✅ Đã cắt xong AOD Hà Nội: {output_tif_path}")
    print(f"🌫️ AOD trung bình ở Hà Nội: {mean_aod:.4f}")
    print(f"🌡️ AOD lớn nhất ở Hà Nội: {max_aod:.4f}")
    print("Min AOD:", min_aod)
    print("Số pixel còn lại trong aod_hanoi:", aod_data.shape)
    print("Số pixel hợp lệ (aod > 0):", np.sum(aod_data > 0))


# ====== Chạy thử tại đây ======
if __name__ == "__main__":
    input_tif = r"C:\Users\Admin\himawari_project_v2\himawari_data_v2\202504\04\00\aod_vietnam_NC_H09_20250404_0000_L2ARP031_FLDK.02401_02401.tif"
    hanoi_shapefile = r"C:\Users\Admin\himawari_project_v2\hanoi\hanoi_shapefile.shp"
    output_tif = input_tif.replace("aod_vietnam", "aod_hanoi")

    crop_hanoi_aod(input_tif, hanoi_shapefile, output_tif)


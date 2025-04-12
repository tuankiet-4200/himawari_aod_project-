import pandas as pd

# Đọc file CSV
df = pd.read_csv("all_station_aod.csv")

# Xoá các cột toàn bộ là NaN
df_cleaned = df.dropna(axis=1, how='all')

# Ghi ra file mới
df_cleaned.to_csv("all_station_aod_cleaned.csv", index=False)

print("Đã xoá các cột rỗng và lưu file mới: all_station_aod_cleaned.csv")

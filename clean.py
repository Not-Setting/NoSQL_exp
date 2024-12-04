import pandas as pd

# 文件路径
hotels_file = "./data/csv/hotels.csv"
rooms_file = "./data/csv/rooms.csv"

# 读取文件
hotels_df = pd.read_csv(hotels_file)
rooms_df = pd.read_csv(rooms_file)

# 检查数据框信息
print("Before cleaning:")
print(f"Hotels dataset:\n{hotels_df.info()}\n")
print(f"Rooms dataset:\n{rooms_df.info()}\n")

# 删除缺失值
cleaned_hotels_df = hotels_df.dropna()
cleaned_rooms_df = rooms_df.dropna()

# 检查清理后数据框信息
print("After cleaning:")
print(f"Hotels dataset:\n{cleaned_hotels_df.info()}\n")
print(f"Rooms dataset:\n{cleaned_rooms_df.info()}\n")

# 保存清理后的数据到新文件
cleaned_hotels_df.to_csv("./data/csv/cleaned_hotels.csv", index=False)
cleaned_rooms_df.to_csv("./data/csv/cleaned_rooms.csv", index=False)

print("Cleaned datasets saved successfully!")

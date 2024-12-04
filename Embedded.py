import time

import pandas as pd
from pymongo import MongoClient
#
# # 1. 加载酒店数据和房间数据
# # 假设酒店信息存储在 hotels.json 文件中，房间信息存储在 rooms.json 文件中
# hotels_df = pd.read_csv('./data/csv/hotels.csv')
# rooms_df = pd.read_csv('./data/csv/rooms.csv')
#
# # hotels_df = hotels_df.drop(columns=['id'], errors='ignore')  # 去掉酒店数据中的 'hotel_id'
# # rooms_df = rooms_df.drop(columns=['id'], errors='ignore')  # 去掉房间数据中的 'room_id'
#
#
# # 2. 将房间信息嵌入到酒店信息中
# # 假设酒店信息有 'hotel_id' 字段，房间信息有 'hotel_id' 字段，我们可以通过 hotel_id 合并数据
# hotels_with_rooms = hotels_df.copy()
#
# # 创建一个空的 'rooms' 列，用来存储每个酒店的房间列表
# hotels_with_rooms['rooms'] = None
#
# # 通过酒店 ID 将房间信息嵌入到酒店信息中
# for idx, hotel in hotels_with_rooms.iterrows():
#     hotel_id = hotel['hotel_id']
#     # 找出与当前酒店 ID 匹配的所有房间
#     rooms_for_hotel = rooms_df[rooms_df['hotel_id'] == hotel_id]
#     # 将房间信息转换为字典并添加到酒店数据中
#     hotels_with_rooms.at[idx, 'rooms'] = rooms_for_hotel.to_dict(orient='records')
#
# hotels_with_rooms.to_json('./data/josn/hotels_with_rooms.json', orient='records', lines=True, force_ascii=False)


hotels_with_rooms = pd.read_json("./data/josn/hotels_with_rooms_noid.json", lines=True)

# 3. 连接到 MongoDB
# 创建一个 MongoClient 实例，连接到 MongoDB 本地数据库
client = MongoClient('mongodb://localhost:27017/')
db = client['hotel_database']  # 选择数据库
collection = db['hotelwithrooms']  # 选择集合
collection.delete_many({})

# 禁用自动索引更新：在插入大量数据时可以暂时禁用背景索引更新
collection.create_index([("hotel_id", 1)], background=False)

# 4. 将酒店和房间信息插入到 MongoDB 中
# 将 hotels_with_rooms DataFrame 转换为字典并插入到 MongoDB 中
hotel_data_dict = hotels_with_rooms.to_dict(orient='records')
# 执行插入操作
start_time = time.time()
explain_result = collection.insert_many(hotel_data_dict)
end_time = time.time()
elapsed_time = end_time - start_time

collection.create_index([("hotel_id", 1)], background=False)

print(f"插入操作耗时: {elapsed_time:.4f} 秒")
print(f'{len(hotel_data_dict)} 条酒店数据已成功导入 MongoDB。')

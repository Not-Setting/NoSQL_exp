
# Re-importing required libraries and reloading data after the interruption
from pymongo import MongoClient
import pandas as pd
import json

def import_csv_to_mongodb(csv_file, db_name, collection_name):
    # 连接到MongoDB服务器
    client = MongoClient("mongodb://localhost:27017/")  # 默认连接本地的MongoDB

    # 选择数据库和集合
    db = client[db_name]
    collection = db[collection_name]

    #清空数据库集合
    collection.delete_many({})

    # 读取CSV文件
    df = pd.read_csv(csv_file)

    # 将DataFrame转换为字典列表
    data = df.to_dict(orient='records')  # 'records' 方式转换，每一行是一个字典

    # 将数据导入MongoDB集合
    collection.insert_many(data)

    print(f"CSV数据已成功导入到 MongoDB 集合 {collection_name}")




db = "hotel_database"
hotels_collection = "hotels"
rooms_collection = "rooms"



# File paths
hotel_room_file = "./data/csv/hotels.csv"
hotel_info_file = "./data/csv/rooms.csv"

# 集合清空
hotels_collection.delete_many({})
rooms_collection.delete_many({})

hotels_dict = {}
rooms_dict = {}

# Load the Excel files into DataFrames
hotel_room_df = pd.read_excel(hotel_room_file)
hotel_info_df = pd.read_excel(hotel_info_file)

# Convert DataFrames to JSON format for MongoDB insertion
hotel_room_json = hotel_room_df.to_dict(orient='records')
hotel_info_json = hotel_info_df.to_dict(orient='records')

# Save the JSON outputs as files
hotel_room_json_path = 'D:\\User\\limbo\\Desktop\\NoSQL实验\\josn\\hotel_room.json'
hotel_info_json_path = 'D:\\User\\limbo\\Desktop\\NoSQL实验\\josn\\hotel_info.json'

with open(hotel_room_json_path, 'w', encoding="utf-8") as file:
    json.dump(hotel_room_json, file, ensure_ascii=False, indent=4)

with open(hotel_info_json_path, 'w', encoding="utf-8") as file:
    json.dump(hotel_info_json, file, ensure_ascii=False, indent=4)



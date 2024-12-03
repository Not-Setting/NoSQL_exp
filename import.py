
# Re-importing required libraries and reloading data after the interruption
from pymongo import MongoClient
import pandas as pd

client = MongoClient("mongodb://localhost:27017/")
db = client["hotel_database"]
hotels_collection = db["hotels"]
rooms_collection = db["rooms"]

# File paths
hotel_room_file = "./data/csv/rooms.csv"
hotel_info_file = "./data/csv/hotels.csv"

# 集合清空
hotels_collection.delete_many({})
rooms_collection.delete_many({})

hotels_dict = {}
rooms_dict = {}

# 读取CSV文件

hotel_room_df = pd.read_csv(hotel_room_file)
hotel_info_df = pd.read_csv(hotel_info_file)

# Convert DataFrames to JSON format for MongoDB insertion
hotel_room_data = hotel_room_df.to_dict(orient='records')
hotel_info_data = hotel_info_df.to_dict(orient='records')

rooms_collection.insert_many(hotel_room_data)
hotels_collection.insert_many(hotel_info_data)





import pandas as pd
import folium
import requests
from folium import Popup
from pymongo import MongoClient

# MongoDB连接
client = MongoClient('mongodb://localhost:27017/')
db = client['hotel_database']  # 选择数据库
collection = db['hotelwithrooms']  # 选择集合

# 百度地图API的地理编码函数
def get_location_by_address(address, api_key):
    # 百度地理编码API的URL
    url = "http://api.map.baidu.com/geocoding/v3/"

    # 请求参数
    params = {
        'address': address,
        'output': 'json',
        'ak': api_key  # 用您的API密钥替换此处
    }

    # 发送请求
    response = requests.get(url, params=params)

    # 解析响应
    if response.status_code == 200:
        result = response.json()
        if result['status'] == 0:  # 百度API返回0表示成功
            location = result['result']['location']
            lng = location['lng']  # 经度
            lat = location['lat']  # 纬度
            return lng, lat
        else:
            print(f"无法获取该地址的经纬度: {result['msg']}")
            return None, None
    else:
        print("请求失败")
        return None, None

# 选择城市进行查询和地图显示
def choosecity(city, api_key):
    # 筛选数据：选择指定城市的高档型酒店
    if city == "beijing":
        data = list(collection.find({"hotel_city_name": '北京'}))
        hotels_data = pd.json_normalize(data)
        filtered_hotels = hotels_data[
            (hotels_data['hotel_grade_text'] == '高档型') &
            (hotels_data['hotel_city_name'].isin(['北京']))
        ]
        m = folium.Map(location=[39.9042, 116.4074], zoom_start=10)
    elif city == "tianjing":
        data = list(collection.find({"hotel_city_name": '天津'}))
        hotels_data = pd.json_normalize(data)
        filtered_hotels = hotels_data[
            (hotels_data['hotel_grade_text'] == '高档型') &
            (hotels_data['hotel_city_name'].isin(['天津']))
        ]
        m = folium.Map(location=[39.0857, 117.1951], zoom_start=10)
    elif city == "chengdu":
        data = list(collection.find({"hotel_city_name": '成都'}))
        hotels_data = pd.json_normalize(data)
        filtered_hotels = hotels_data[
            (hotels_data['hotel_grade_text'] == '高档型') &
            (hotels_data['hotel_city_name'].isin(['成都']))
        ]
        m = folium.Map(location=[39.0857, 117.1951], zoom_start=10)
    else:
        print("Error: Unsupported city")
        return

    # 添加经纬度列
    filtered_hotels['lng'] = 0
    filtered_hotels['lat'] = 0

    # 获取经纬度
    for idx, row in filtered_hotels.iterrows():
        try:
            # 组合酒店名称和区域信息为地址
            address = f"{row['hotel_name']} {row['hotel_location_info']} {row['hotel_city_name']}"
            lng, lat = get_location_by_address(address, api_key)

            if lng and lat:
                filtered_hotels.loc[idx, 'lng'] = lng
                filtered_hotels.loc[idx, 'lat'] = lat

        except Exception as e:
            print(f"Error for {row['hotel_location_info']}: {e}")

    # 删除没有获取到经纬度的数据
    filtered_hotels = filtered_hotels.dropna(subset=['lat', 'lng'])

    # 在地图上标记最低房价的酒店
    for idx, row in filtered_hotels.iterrows():
        hotel_name = row['hotel_name']
        hotel_location = [row['lat'], row['lng']]

        # 获取该酒店的最低房价
        min_price = min([room['room_price'] for room in row['rooms']])

        # 获取房间的第一张图片（如果有的话）
        room_image_url = row['rooms'][0].get('room_image_url', 'https://via.placeholder.com/150')

        # 创建Popup文本，显示房间价格和图片
        popup_text = f"<b>{hotel_name}</b><br>最低房间价格: {min_price}元<br>"
        popup_text += f"<img src='{room_image_url}' alt='Hotel Image' style='width:150px;height:auto;'>"

        # 在酒店位置添加标记，显示最低房价和房间图片
        folium.Marker(
            location=hotel_location,
            popup=Popup(popup_text, max_width=300)
        ).add_to(m)

    # 保存为HTML文件
    output_path = f'./output/html/{city}_hotel_rooms_with_min_price_and_image.html'
    m.save(output_path)

    print(f"酒店地图已保存到 {output_path}")

# 设置API密钥
api_key = "d2VPDIAKHdEM5VAStBXH4LXN8cWfVwXM"
city = "beijing"

#choosecity(city, api_key)

city = "chengdu"
choosecity(city, api_key)


import pandas as pd
import folium
import requests
from folium.plugins import HeatMap
from pymongo import MongoClient


client = MongoClient('mongodb://localhost:27017/')
db = client['hotel_database']  # 选择数据库
collection = db['hotelwithrooms']  # 选择集合

hotels_data =list(collection.find({}))


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

# 选择城市进行热力图建模
def choosecity(city,api_key):
    # 读取数据
    #file_path = './data/csv/cleaned_hotels.csv'  # 请根据实际路径调整



    # 筛选数据
    if city == "beijing":
        data = list(collection.find({"hotel_city_name":'北京'}))
        hotels_data = pd.json_normalize(data)
        filtered_hotels = hotels_data[
            (hotels_data['hotel_grade_text'] == '高档型') &
            (hotels_data['hotel_city_name'].isin(['北京']))
            ]
        m = folium.Map(location=[39.9042, 116.4074], zoom_start=10)
    elif city== "tianjing":
        data = list(collection.find({"hotel_city_name":'天津'}))
        hotels_data = pd.json_normalize(data)
        filtered_hotels = hotels_data[
            (hotels_data['hotel_grade_text'] == '高档型') &
            (hotels_data['hotel_city_name'].isin(['天津']))
            ]
        m = folium.Map(location=[39.0857, 117.1951], zoom_start=10)
    else:
        print("error")
        # 添加经纬度列

    filtered_hotels['lng']=0
    filtered_hotels['lat']=0
    # API密钥
   # 使用您自己的API密钥

    # 获取经纬度
    for idx, row in filtered_hotels.iterrows():
        try:
            # 组合酒店名称和区域信息为地址
            address = f"{row['hotel_name']} {row['hotel_location_info']} {row['hotel_city_name']}"
            lng, lat = get_location_by_address(address, api_key)

            if lng and lat:
                filtered_hotels.loc[idx, 'lng'] = lng
                filtered_hotels.loc[idx, 'lat'] = lat
                # print(lng,lat)

        except Exception as e:
            print(f"Error for {row['hotel_location_info']}: {e}")

    # 删除没有获取到经纬度的数据
    filtered_hotels = filtered_hotels.dropna(subset=['lat', 'lng'])

    # 创建热力图
    # 初始化地图，默认北京


    # 添加热力图
    heat_data = filtered_hotels[['lat', 'lng']].values.tolist()
    HeatMap(heat_data).add_to(m)

    # 保存为 HTML
    output_path = './output/html/'+city+'_hotel_heatmap.html'  # 根据需要更改输出路径
    m.save(output_path)

    print(f"热力图已保存到 {output_path}")

api_key = "XXXXXXXXX"
city = "beijing"

choosecity(city,api_key)
city = "tianjing"

choosecity(city,api_key)

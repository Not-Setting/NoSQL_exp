import pandas as pd
import re
from pymongo import MongoClient
import seaborn as sns
import matplotlib.pyplot as plt

# MongoDB 连接设置
client = MongoClient('mongodb://localhost:27017/')
db = client['hotel_database']  # 选择数据库
collection = db['hotelwithrooms']  # 选择集合

# 解析房间面积函数
def parse_room_area(area):
    """
    解析房间面积字段，将其转换为数值。
    :param area: 房间面积字符串（如 '28-40㎡' 或 '65㎡'）
    :return: 数值型房间面积，若解析失败则返回 None
    """
    if isinstance(area, str):
        # 提取范围描述
        range_match = re.match(r"(\d+)-(\d+)", area)
        if range_match:
            lower = float(range_match.group(1))
            upper = float(range_match.group(2))
            return (lower + upper) / 2  # 返回范围的中值
        # 提取单一数值
        single_match = re.match(r"(\d+)", area)
        if single_match:
            return float(single_match.group(1))
    return None

def task1(city, grade):
    """
    分析不同酒店类型下房间面积与房间价格的关系
    :param city: 城市名称
    :param grade: 酒店等级（如高档型、经济型等）
    """
    # 从 MongoDB 获取数据
    cursor = collection.find(
        {"hotel_city_name": city, "hotel_grade_text": grade},
        {
            "hotel_grade_text": 1,
            "rooms.room_area": 1,
            "rooms.room_price": 1,
        }
    )
    data = list(cursor)

    # 将数据转换为 DataFrame
    hotels = []
    for hotel in data:
        for room in hotel.get("rooms", []):
            hotels.append({
                "hotel_grade_text": hotel.get("hotel_grade_text"),
                "room_area": room.get("room_area"),
                "room_price": room.get("room_price"),
            })

    df = pd.DataFrame(hotels)

    # 数据清洗：解析房间面积和删除缺失值
    df['room_area'] = df['room_area'].apply(parse_room_area)
    df = df.dropna(subset=['room_area', 'room_price'])

    # 可视化：绘制散点图
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='room_area', y='room_price', hue='hotel_grade_text')
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
    plt.rcParams["axes.unicode_minus"] = False  # 避免负号显示为方块
    plt.title(f'{grade} 酒店房间面积与价格的关系 ({city})')
    plt.xlabel('房间面积（平方米）')
    plt.ylabel('房间价格（元）')
    plt.legend(title='酒店类型')
    plt.savefig('./output/figs/task4_1'+city+grade+'.eps')
    plt.savefig('./output/figs/task4_'+city+grade+'1.png', dpi=300)
    plt.show()
    # 返回清洗后的数据框以供进一步分析
    return df





# 示例调用
city = "北京"  # 修改为 'tianjing' 可分析天津数据
grade = "高档型"
df_cleaned = task1(city, grade)

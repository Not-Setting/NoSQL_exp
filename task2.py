import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pymongo import MongoClient


def plot_score_vs_price(hotels_data):
    # 将数据转换为 DataFrame
    hotels_df = pd.json_normalize(hotels_data, record_path='rooms',
                                  meta=['hotel_score', 'hotel_name', 'hotel_city_name'])

    # 检查是否包含有效数据
    if 'hotel_score' not in hotels_df.columns or hotels_df['hotel_score'].isnull().all():
        print("未找到有效的 'hotel_score' 数据。")
        return

    if 'room_price' not in hotels_df.columns or hotels_df['room_price'].isnull().all():
        print("未找到有效的 'room_price' 数据。")
        return

    # 去除缺失值
    hotels_df = hotels_df.dropna(subset=['hotel_score', 'room_price'])

    # 按酒店计算最贵房间价格
    max_price_per_hotel = hotels_df.groupby('hotel_name').agg({
        'hotel_score': 'first',  # 每个酒店的评分
        'room_price': 'max',  # 最贵房间价格
        'hotel_city_name': 'first'  # 取第一个城市名称（每个酒店的城市应相同）
    }).reset_index()

    # 设置 Seaborn 配色
    plt.figure(figsize=(12, 7))
    sns.scatterplot(x='hotel_score', y='room_price', data=max_price_per_hotel,
                    hue='hotel_city_name', palette='Set1', s=100, alpha=0.8)

    plt.title('酒店评分与房间最高价格的关系', fontsize=16, weight='bold', color='darkblue')
    plt.xlabel('酒店评分', fontsize=14)
    plt.ylabel('房间最高价格', fontsize=14)

    plt.legend(title='城市', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
    plt.rcParams["axes.unicode_minus"] = False  # 避免负号显示为方块

    plt.tight_layout()

    plt.savefig('./output/figs/hotel_score_vs_price_by_city.png', dpi=300)
    plt.show()


# 从 MongoDB 获取数据
client = MongoClient('mongodb://localhost:27017/')  # 替换为你的 MongoDB 连接 URI
db = client['hotel_database']  # 替换为你的数据库名称
collection = db['hotelwithrooms']  # 替换为你的集合名称

hotels_data = list(collection.find({}))

# 生成图表
plot_score_vs_price(hotels_data)


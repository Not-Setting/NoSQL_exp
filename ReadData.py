import warnings

import folium
import numpy as np
import requests
from folium.plugins import HeatMap
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 忽略 FutureWarning
warnings.simplefilter(action='ignore', category=FutureWarning)

class DataShower:
    def __init__(self):
        # 连接到 MongoDB
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["hotel_database"]
        self.hotels_collection = self.db["hotels"]
        self.rooms_collection = self.db["rooms"]
        # 从集合中读取数据
        self.hotels_data = list(self.hotels_collection.find({}))

        plt.rcParams["font.sans-serif"] = ["SimHei"]  # 使用黑体（SimHei）显示中文
        plt.rcParams["axes.unicode_minus"] = False  # 避免负号显示为方块

    def task_1(self):
        # 将数据转换为 DataFrame
        hotels_df = pd.json_normalize(self.hotels_data)

        # 检查是否包含有效数据
        if 'hotel_score' not in hotels_df.columns or hotels_df['hotel_score'].isnull().all():
            print("No valid 'hotel_score' data found.")
            return

        # 处理缺失值
        hotels_df['hotel_score'] = hotels_df['hotel_score'].dropna()

        # 计算统计数值
        mean_score = hotels_df['hotel_score'].mean()
        median_score = hotels_df['hotel_score'].median()
        max_score = hotels_df['hotel_score'].max()
        min_score = hotels_df['hotel_score'].min()
        mode_score = hotels_df['hotel_score'].mode()
        # 标准分数
        std_score = hotels_df['hotel_score'].std()
        # 数据分布偏度
        skewness = hotels_df['hotel_score'].skew()
        # 峰度
        kurtosis = hotels_df['hotel_score'].kurtosis()

        # 分位数
        q25 = hotels_df['hotel_score'].quantile(0.25)
        q75 = hotels_df['hotel_score'].quantile(0.75)

        # 将众数转换为字符串，限制显示数量
        mode_score_display = ', '.join(map(str, mode_score[:3]))
        if len(mode_score) > 3:
            mode_score_display += ', ...'

        # 设置图形主题
        sns.set_theme(style="whitegrid")
        plt.figure(figsize=(12, 7))
        ax = sns.histplot(hotels_df['hotel_score'], bins=20, kde=True, color='steelblue', alpha=0.8)

        # 在图中添加垂直线标注
        ax.axvline(mean_score, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_score:.2f}')
        ax.axvline(median_score, color='orange', linestyle='--', linewidth=2, label=f'Median: {median_score:.2f}')
        for m in mode_score:
            ax.axvline(m, color='green', linestyle='--', linewidth=1, label=f'Mode: {m}')

        # 添加统计信息
        stats_text = '\n'.join([
            f'Mean: {mean_score:.2f}',
            f'Median: {median_score:.2f}',
            f'Max: {max_score}',
            f'Min: {min_score}',
            f'Std Dev: {std_score:.2f}',
            f'Skewness: {skewness:.2f}',
            f'Kurtosis: {kurtosis:.2f}',
            f'25% Quantile: {q25:.2f}',
            f'75% Quantile: {q75:.2f}',
            f'Mode: {mode_score_display}'
        ])
        plt.text(1.02, 0.5, stats_text, transform=ax.transAxes, fontsize=12, verticalalignment='center',
                 bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgrey", edgecolor="gray"))

        # 美化标题和标签
        plt.title('Hotel Score Distribution', fontsize=16, weight='bold', color='darkblue')
        plt.xlabel('Score', fontsize=14)
        plt.ylabel('Frequency', fontsize=14)
        plt.legend(loc='upper left', fontsize=12)
        plt.tight_layout()
        plt.show()

    def task_2(self):
        # 将数据转换为 DataFrame
        hotels_df = pd.json_normalize(self.hotels_data, record_path="rooms", meta=[
            "hotel_id", "hotel_name", "hotel_score", "hotel_location_info",
            "hotel_grade_text", "hotel_comment_desc", "hotel_city_name"
        ])

        # 计算每个酒店的最高房间价格，并按评分和酒店等级进行分组
        price_score_df = hotels_df.groupby(["hotel_score", "hotel_grade_text"]).agg(
            max_room_price=("room_price", "max")
        ).reset_index()

        # 可视化评分与房间价格的关系
        plt.figure(figsize=(12, 8))  # 增大图表尺寸

        # 使用散点图，调整点的大小、透明度和颜色
        scatter = sns.scatterplot(data=price_score_df, x="hotel_score", y="max_room_price",
                                  hue="hotel_grade_text", palette="viridis", s=100, alpha=0.7, edgecolor="black")

        # 优化图表外观
        plt.title("Relationship between Hotel Ratings and Maximum Room Rates", fontsize=16, weight='bold', color='darkblue')
        plt.xlabel("Hotel Score", fontsize=14)
        plt.ylabel("Maximum Room Price (USD)", fontsize=14)

        # 增加网格线，并设置透明度
        plt.grid(True, linestyle='--', alpha=0.6)

        # 增加颜色条（legend）并调整位置
        plt.legend(title="Hotel Grade", loc="upper left", fontsize=12, title_fontsize=14)

        # 美化坐标轴
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)

        # 优化布局
        plt.tight_layout()

        # 显示图表
        plt.show()

    def task_3(self, city_name, mode=1):
        if self.geo_data(city_name,mode):
            if city_name == "北京":
                check_name = "beijing"
                location = [39.9042, 116.4074]
            elif city_name == "天津":
                check_name = "tianjin"
                location = [39.0857, 117.1951]
            else:
                raise ValueError("不支持这个城市")
            geo_path = check_name + '_geo_data.csv'
            geo_df = pd.read_csv(geo_path)
            m = folium.Map(location=location, zoom_start=10)
            heat_data = [[row['lat'], row['lng']] for index, row in geo_df.iterrows()]
            HeatMap(heat_data).add_to(m)
            heat_path = check_name + '_heat_map.html'
            m.save(heat_path)
        else:
            print("数据不完备,请根据提示再试")


    def task_4_1(self):
        # 将数据转换为 DataFrame
        hotels_df = pd.json_normalize(self.hotels_data)
        # 计算每个城市的平均评分
        city_score_df = hotels_df.groupby("hotel_city_name")["hotel_score"].mean().reset_index()
        city_score_df = city_score_df.sort_values(by="hotel_score", ascending=False)

        print("各城市酒店平均评分:")
        print(city_score_df)

        # 可视化
        plt.figure(figsize=(10, 6))
        sns.barplot(data=city_score_df, x="hotel_city_name", y="hotel_score", palette="coolwarm")
        plt.xticks(rotation=90)
        plt.title("各城市酒店平均评分")
        # 设置 Y 轴范围和刻度
        plt.ylim(4.5, 5)  # 自定义 Y 轴范围
        plt.yticks(np.arange(4.5, 5.1, 0.05))  # 设置刻度间隔为 0.05
        plt.xlabel("城市")
        plt.ylabel("平均评分")
        plt.show()

    def task_4_2(self):
        # 将数据转换为 DataFrame
        hotels_df = pd.json_normalize(self.hotels_data)
        # 计算不同等级的评分平均值
        grade_score_df = hotels_df.groupby("hotel_grade_text")["hotel_score"].mean().reset_index()
        grade_score_df = grade_score_df.sort_values(by="hotel_score", ascending=False)

        print("不同等级酒店的评分:")
        print(grade_score_df)

        # 可视化
        plt.figure(figsize=(8, 5))
        sns.boxplot(data=hotels_df, x="hotel_grade_text", y="hotel_score", palette="Set3")
        plt.title("酒店等级与评分分布")
        plt.xlabel("酒店等级")
        plt.ylabel("评分")
        plt.show()

    def _geo_data_init(self,city_name):
        # 将数据转换为 DataFrame
        hotels_df = pd.json_normalize(self.hotels_data)
        hotels_df.drop('hotel_score', axis=1, inplace=True)
        hotels_df.drop('hotel_image_id', axis=1, inplace=True)
        hotels_df.drop('hotel_comment_desc', axis=1, inplace=True)
        hotels_df.drop('rooms', axis=1, inplace=True)
        hotels_df = hotels_df[hotels_df['hotel_city_name'] == city_name]
        hotels_df = hotels_df[hotels_df['hotel_grade_text'] == "高档型"]
        # 提取地址
        hotels_df[['secondary_address', 'primary_address']] = hotels_df['hotel_location_info'].str.split(' · ', expand=True)
        hotels_df['secondary_address'] = hotels_df['secondary_address'].str.replace('近', '', regex=False)
        hotels_df['lat'] = ''
        hotels_df['lng'] = ''
        hotels_df['province'] = ''
        hotels_df['city'] = ''
        hotels_df['area'] = ''
        if city_name == "北京":
            city_name = "beijing"
        elif city_name == "天津":
            city_name = "tianjin"
        path = city_name+'_geo_data.csv'
        hotels_df.to_csv(path, index=False)

    # mode:
    # 1:使用hotel_name进行处理
    # 2:使用hotel_location_info的前缀进行处理
    def geo_data(self,city_name,mode=1):
        check_name = None
        if city_name == "北京":
            check_name = "beijing"
        elif city_name == "天津":
            check_name = "tianjin"
        path = check_name + '_geo_data.csv'
        if not os.path.exists(path):
            self._geo_data_init(city_name)
        geo_df = pd.read_csv(path)

        params = {
            "query": "",
            "region": city_name,
            "output": "json",
            "ak": "XXXXXX",
        }

        for index,row in geo_df.iterrows():
            if pd.isna(row['lat']):
                url = "https://api.map.baidu.com/place/v2/search"
                if mode == 1:
                    params['query'] = row['hotel_name']
                else:
                    params['query'] = row['secondary_address']
                response = requests.get(url=url, params=params)
                # 查看返回的状态码
                status_code = response.json()['status']
                print(response.json())
                if status_code != 0:
                    continue
                try:
                    geo_df.at[index, 'province'] = response.json()['results'][0]['province']
                    geo_df.at[index, 'city'] = response.json()['results'][0]['city']
                    geo_df.at[index, 'area'] = response.json()['results'][0]['area']
                except KeyError:
                    print(row)
                    continue
                except IndexError:
                    print(row)
                    continue
                if ((city_name == "北京" and response.json()['results'][0]['city'] != "北京市")
                        or (city_name == "天津" and response.json()['results'][0]['city'] != "天津市")):
                    geo_df.at[index, 'province'] = None
                    geo_df.at[index, 'city'] = None
                    geo_df.at[index, 'area'] = None
                    print(row)
                    continue
                geo_df.at[index, 'lat'] = response.json()['results'][0]['location']['lat']
                geo_df.at[index, 'lng'] = response.json()['results'][0]['location']['lng']
                geo_df.to_csv(path, index=False)

        # check
        if (geo_df['lat'].isnull().sum() == 0 and geo_df['lng'].isnull().sum() == 0
                and geo_df['province'].isnull().sum() == 0 and geo_df['city'].isnull().sum() == 0
                and geo_df['area'].isnull().sum() == 0):
            return True
        else:
            print("存在脏数据行,请更换mode或手工补充数据!")
            return False


if __name__ == "__main__":
    dataShower = DataShower()
    dataShower.task_2()


from os.path import curdir

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pymongo import MongoClient




def plot_hotel_scores(hotels_data):
    # 将数据转换为 DataFrame
    hotels_df = pd.json_normalize(hotels_data)

    # 检查是否包含有效数据
    if 'hotel_score' not in hotels_df.columns or hotels_df['hotel_score'].isnull().all():
        print("未找到有效的 'hotel_score' 数据。")
        return

    # 处理缺失值
    hotels_df['hotel_score'] = hotels_df['hotel_score'].dropna()

    # 计算统计数值
    mean_score = hotels_df['hotel_score'].mean()
    median_score = hotels_df['hotel_score'].median()
    max_score = hotels_df['hotel_score'].max()
    min_score = hotels_df['hotel_score'].min()
    mode_score = hotels_df['hotel_score'].mode()[0]  # 取第一个众数

    # 绘制评分分布图（无趋势线）
    sns.set_theme(style="whitegrid")
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
    plt.rcParams["axes.unicode_minus"] = False  # 避免负号显示问题
    plt.figure(figsize=(12, 7))

    ax = sns.histplot(hotels_df['hotel_score'], bins=20, color='steelblue', alpha=0.8)
    plt.title('酒店评分分布', fontsize=16, weight='bold', color='darkblue', fontname='Microsoft YaHei')
    plt.xlabel('评分', fontsize=14)
    plt.ylabel('出现次数', fontsize=14)

    # 在柱状图上标注数据
    for patch in ax.patches:
        if patch.get_height() > 0:  # 仅标注非零高度的柱子
            ax.text(
                patch.get_x() + patch.get_width() / 2,  # X 坐标为柱子中心
                patch.get_height(),  # Y 坐标为柱子高度
                f'{int(patch.get_height())}',  # 标注值
                ha='center', va='bottom', fontsize=10, color='black', weight='bold'
            )

    plt.tight_layout()

    # 保存第一张图片
    plt.savefig('./output/figs/task1_distribution.png', dpi=300)
    plt.show()

    # 绘制统计信息柱状图
    plt.figure(figsize=(10, 6))

    stats_values = [mean_score, median_score, mode_score, max_score, min_score]
    stats_labels = ['平均值', '中位数', '众数', '最大值', '最小值']

    barplot = sns.barplot(x=stats_labels, y=stats_values, palette='viridis')

    # 在每个柱子上标注数据
    for index, value in enumerate(stats_values):
        barplot.text(
            index, value + 0.1,  # X 为柱子的索引，Y 为柱子高度稍高的位置
            f'{value:.2f}',  # 标注值
            ha='center', va='bottom', fontsize=12, color='black', weight='bold'
        )

    plt.title('酒店评分统计信息', fontsize=16, weight='bold', color='darkblue', fontname='Microsoft YaHei')
    plt.ylabel('评分', fontsize=14)
    plt.xlabel('统计指标', fontsize=14)
    plt.ylim(4, 5.2)
    plt.tight_layout()

    # 保存第二张图片
    plt.savefig('./output/figs/task1_stats_barplot.png', dpi=300)
    plt.show()


# 生成图表

client = MongoClient('mongodb://localhost:27017/')
db = client['hotel_database']
collection = db['hotelwithrooms']
cursor = collection.find({},{"hotel_score":1})
hotels_data = list(cursor)
cursor.close()


# cursor = collection.find({},{"hotel_score":1,"hotel_city_name":1,"room_price_range":1})
# hotels_data = list(cursor)
# cursor.close()


plot_hotel_scores(hotels_data)

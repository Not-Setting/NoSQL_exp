import tkinter as tk
from tkinter import messagebox
from pymongo import MongoClient
import pandas as pd

# 连接到 MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['hotel_database']
collection = db['hotelwithrooms']


# 查询函数：根据酒店名称查询
def query_by_hotel_name():
    hotel_name = hotel_name_entry.get()
    if not hotel_name:
        messagebox.showerror("输入错误", "请输入酒店名称")
        return
    hotel_name_entry.delete(0, tk.END)  # 清空输入框

    try:
        result = collection.find({"hotel_name": {"$regex": hotel_name, "$options": "i"}})
        display_results(result, query_type="default")
    except Exception as e:
        messagebox.showerror("数据库错误", f"查询过程中出现问题: {str(e)}")


# 查询函数：根据评分范围查询
def query_by_score():
    try:
        min_score = float(min_score_entry.get())
        max_score = float(max_score_entry.get())
    except ValueError:
        messagebox.showerror("输入错误", "请输入有效的评分范围")
        return

    min_score_entry.delete(0, tk.END)  # 清空输入框
    max_score_entry.delete(0, tk.END)  # 清空输入框

    try:
        result = collection.find({"hotel_score": {"$gte": min_score, "$lte": max_score}})
        display_results(result, query_type="default")
    except Exception as e:
        messagebox.showerror("数据库错误", f"查询过程中出现问题: {str(e)}")


# 查询函数：根据城市查询
def query_by_city():
    city_name = city_name_entry.get()
    if not city_name:
        messagebox.showerror("输入错误", "请输入城市名称")
        return
    city_name_entry.delete(0, tk.END)  # 清空输入框

    try:
        result = collection.find({"hotel_city_name": {"$regex": city_name, "$options": "i"}})
        display_results(result, query_type="default")
    except Exception as e:
        messagebox.showerror("数据库错误", f"查询过程中出现问题: {str(e)}")


# 查询函数：查询最贵的房间价格
def query_max_price():
    try:
        result = collection.aggregate([
            {"$unwind": "$rooms"},
            {"$group": {
                "_id": "$hotel_name",
                "hotel_score": {"$first": "$hotel_score"},
                "max_price": {"$max": "$rooms.room_price"}
            }}
        ])
        display_results(result, query_type="max_price")
    except Exception as e:
        messagebox.showerror("数据库错误", f"查询过程中出现问题: {str(e)}")


# 查询函数：查询城市的酒店数量
def query_city_hotel_count():
    try:
        result = collection.aggregate([
            {"$group": {
                "_id": "$hotel_city_name",
                "hotel_count": {"$sum": 1}
            }}
        ])
        display_results(result, query_type="city_hotel_count")
    except Exception as e:
        messagebox.showerror("数据库错误", f"查询过程中出现问题: {str(e)}")


# 显示查询结果
def display_results(result, query_type=None):
    result_text.delete(1.0, tk.END)

    if not result:
        result_text.insert(tk.END, "没有找到符合条件的酒店信息。\n")
        return

    if query_type == "max_price":
        for entry in result:
            text = f"酒店名称: {entry.get('_id', '未知')}, "
            text += f"评分: {entry.get('hotel_score', '未知')}, "
            text += f"最贵房间价格: {entry.get('max_price', '未知')}\n"
            result_text.insert(tk.END, text)
    elif query_type == "city_hotel_count":
        for entry in result:
            text = f"城市: {entry.get('_id', '未知')}, "
            text += f"酒店数量: {entry.get('hotel_count', '未知')}\n"
            result_text.insert(tk.END, text)
    else:
        for entry in result:
            text = f"酒店名称: {entry.get('hotel_name', '未知')}, "
            text += f"评分: {entry.get('hotel_score', '未知')}\n"
            result_text.insert(tk.END, text)


# 创建 GUI 窗口
window = tk.Tk()
window.title("酒店查询系统")
window.geometry("600x400")

# 输入框和标签
tk.Label(window, text="酒店名称：").grid(row=0, column=0, padx=10, pady=10)
hotel_name_entry = tk.Entry(window, width=30)
hotel_name_entry.grid(row=0, column=1)

tk.Label(window, text="最低评分：").grid(row=1, column=0, padx=10, pady=10)
min_score_entry = tk.Entry(window, width=30)
min_score_entry.insert(0, "0")  # 默认最低评分
min_score_entry.grid(row=1, column=1)

tk.Label(window, text="最高评分：").grid(row=2, column=0, padx=10, pady=10)
max_score_entry = tk.Entry(window, width=30)
max_score_entry.insert(0, "5")  # 默认最高评分
max_score_entry.grid(row=2, column=1)

tk.Label(window, text="城市：").grid(row=3, column=0, padx=10, pady=10)
city_name_entry = tk.Entry(window, width=30)
city_name_entry.grid(row=3, column=1)

# 查询按钮
tk.Button(window, text="按酒店名称查询", command=query_by_hotel_name).grid(row=4, column=0, padx=10, pady=10)
tk.Button(window, text="按评分范围查询", command=query_by_score).grid(row=4, column=1, padx=10, pady=10)
tk.Button(window, text="按城市查询", command=query_by_city).grid(row=4, column=2, padx=10, pady=10)
tk.Button(window, text="查询最贵房间", command=query_max_price).grid(row=5, column=0, padx=10, pady=10)
tk.Button(window, text="查询城市酒店数量", command=query_city_hotel_count).grid(row=5, column=1, padx=10, pady=10)

# 显示查询结果的文本框
result_text = tk.Text(window, height=10, width=70)
result_text.grid(row=6, column=0, columnspan=3, padx=10, pady=10)

# 启动 GUI 窗口
window.mainloop()

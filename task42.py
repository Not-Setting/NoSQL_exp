import tkinter as tk
from tkinter import messagebox
from pymongo import MongoClient

# 连接到 MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['hotel_database']
collection = db['hotelwithrooms']


# 查询函数：根据多个条件查询
def query_by_conditions():
    # 获取输入框的值
    hotel_name = hotel_name_entry.get()
    min_score = min_score_entry.get()
    max_score = max_score_entry.get()
    city_name = city_name_entry.get()

    # 动态构建查询条件
    query_conditions = {}

    # 酒店名称
    if hotel_name:
        query_conditions["hotel_name"] = {"$regex": hotel_name, "$options": "i"}

    # 评分范围
    if min_score and max_score:
        try:
            min_score = float(min_score)
            max_score = float(max_score)
            query_conditions["hotel_score"] = {"$gte": min_score, "$lte": max_score}
        except ValueError:
            messagebox.showerror("输入错误", "评分范围必须是数字")
            return

    # 城市名称
    if city_name:
        query_conditions["hotel_city_name"] = {"$regex": city_name, "$options": "i"}

    # 如果没有输入任何查询条件，提示用户至少输入一个查询条件
    if not query_conditions:
        messagebox.showerror("输入错误", "请至少输入一个查询条件")
        return

    # 执行查询
    try:
        result = collection.aggregate([
            {"$match": query_conditions},  # 使用构建的动态查询条件
            {"$unwind": "$rooms"},
            {"$group": {
                "_id": "$hotel_name",  # 使用酒店名称作为分组字段
                "hotel_score": {"$first": "$hotel_score"},
                "hotel_city_name": {"$first": "$hotel_city_name"},
                "min_price": {"$min": "$rooms.room_price"},
                "max_price": {"$max": "$rooms.room_price"}
            }}
        ])

        result = list(result)  # 转换为列表以便排序
        apply_sorting(result)
        display_results(result, query_type="default")
    except Exception as e:
        messagebox.showerror("数据库错误", f"查询过程中出现问题: {str(e)}")


# 排序函数
def apply_sorting(result):
    sort_order = sort_option.get()  # 获取排序方式
    reverse = sort_order in ["评分降序", "最贵房间降序"]  # 判断是否降序

    # 按不同字段排序
    if sort_order == "评分升序":
        result.sort(key=lambda x: x.get("hotel_score", 0), reverse=False)
    elif sort_order == "评分降序":
        result.sort(key=lambda x: x.get("hotel_score", 0), reverse=True)
    elif sort_order == "最贵房间降序":
        result.sort(key=lambda x: x.get("max_price", 0), reverse=True)
    elif sort_order == "最便宜房间升序":
        result.sort(key=lambda x: x.get("min_price", 0), reverse=False)


# 显示查询结果
def display_results(result, query_type=None):
    result_text.delete(1.0, tk.END)

    if not result:
        result_text.insert(tk.END, "没有找到符合条件的酒店信息。\n")
        return

    for entry in result:
        text = f"酒店名称: {entry.get('_id', '未知')}, "
        text += f"评分: {entry.get('hotel_score', '未知')}, "
        text += f"城市: {entry.get('hotel_city_name', '未知')}, "
        text += f"最便宜房间价格: {entry.get('min_price', '未知')}, "
        text += f"最贵房间价格: {entry.get('max_price', '未知')}\n"
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

# 排序选择
tk.Label(window, text="排序方式：").grid(row=4, column=0, padx=10, pady=10)
sort_option = tk.StringVar(window)
sort_option.set("评分升序")  # 默认排序方式为评分升序
sort_menu = tk.OptionMenu(window, sort_option, "评分升序", "评分降序", "最贵房间降序", "最便宜房间升序")
sort_menu.grid(row=4, column=1)

# 查询按钮
tk.Button(window, text="查询", command=query_by_conditions).grid(row=5, column=0, columnspan=3, padx=10, pady=10)

# 显示查询结果的文本框
result_text = tk.Text(window, height=10, width=70)
result_text.grid(row=6, column=0, columnspan=3, padx=10, pady=10)

# 启动 GUI 窗口
window.mainloop()

import pandas as pd


def xlsx_to_csv(xlsx_file, csv_file):
    try:
        # 使用pandas读取xlsx文件，强制将所有数据作为字符串类型读取
        df = pd.read_excel(xlsx_file, sheet_name=0, dtype=str, engine='openpyxl')

        # 填充空值为 NaN 或其他指定值
        df.fillna('NaN', inplace=True)  # 将 NaN 填充为空字符串，您也可以填充为其他默认值

        # 将DataFrame写入csv文件
        df.to_csv(csv_file, index=False)  # index=False 表示不写入行号
        print(f"文件已成功转换为 {csv_file}")
    except Exception as e:
        print(f"转换失败: {e}")

# 输入文件路径
hotels_xlsx_file = './data/hotel_info.xlsx'  # 替换为您的xlsx文件路径
rooms_xlsx_file = './data/hotel_room.xlsx'  # 替换为您的xlsx文件路径

hotels_csv_file = './data/csv/hotels.csv'  # 替换为输出的csv文件路径
rooms_csv_file = './data/csv/rooms.csv'  # 替换为输出的csv文件路径

# 调用函数进行转换
xlsx_to_csv(hotels_xlsx_file, hotels_csv_file)
xlsx_to_csv(rooms_xlsx_file, rooms_csv_file)
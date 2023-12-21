import pandas as pd
import glob
import os
import json
import requests
from scipy.spatial.distance import cdist
from datetime import datetime
from urllib.parse import quote_plus
import numpy as np
from random import randint, choices
# 指定文件夹路径
def find_coordinates_by_road_name(road_name, user_agent="my-application"):
    # 对道路名称进行URL编码
    encoded_road_name = quote_plus(road_name)
    # 香港地理范围的大致边界框, 格式：left,bottom,right,top (min lon, min lat, max lon, max lat)
    viewbox = "113.818,22.146,114.502,22.614"
    base_url = f"https://nominatim.openstreetmap.org/search.php?q={encoded_road_name}&format=json&viewbox={viewbox}&bounded=1"

    headers = {
        'User-Agent': user_agent
    }

    # 发送请求并获取响应
    response = requests.get(base_url, headers=headers)
    results = response.json()

    # 检查是否有结果返回
    if results:
        # 提取第一个结果的地理坐标
        coordinates = {
            "latitude": results[0]["lat"],
            "longitude": results[0]["lon"]
        }
        print(road_name,coordinates)
        return coordinates
    else:
        # 如果没有结果，返回None
        print(road_name,"None")
        return None

def calculate_num_bus(row):
    # 提取对应时间的车流量
    traffic_hour= row['hour']
    traffic_volume = row[f'{traffic_hour}']
    # 计算出租车数量的比例
    num_bus = (row['Bus'] / 100) * traffic_volume if traffic_volume else 0
    return num_bus


def calculate_num_taxi(row):
    # 提取对应时间的车流量
    traffic_hour= row['hour']
    traffic_volume = row[f'{traffic_hour}']
    print(traffic_volume)
    # 计算出租车数量的比例
    num_taxi = (row['Taxi'] / 100) * traffic_volume if traffic_volume else 0
    return num_taxi


def calculate_num_cargo(row):
    # 提取对应时间的车流量
    traffic_hour= row['hour']
    traffic_volume = row[f'{traffic_hour}']
    print(row)
    # 计算出租车数量的比例
    num_cargo = (row['Cargo'] / 100) * traffic_volume if traffic_volume else 0
    return num_cargo


def calculate_num_priate_veh(row):
    # 提取对应时间的车流量
    traffic_hour= row['hour']
    traffic_volume = row[f'{traffic_hour}']
    print(traffic_volume)
    # 计算出租车数量的比例
    num_cargo = (row['Private_Veh'] / 100) * traffic_volume if traffic_volume else 0
    return num_cargo


def find_nearest_station(row_):
    # 计算距离\
    distances = cdist(
        np.array([(row_['origin_coord_lat'], row_['origin_coord_lng'])]),
        atc_data[['latitude', 'longitude']].values,
        metric='euclidean'
    )
    # 找到最近的站点
    nearest_index = np.argmin(distances)
    return atc_data.iloc[nearest_index]['station_id']


def generate_times(row1,num_times=1):
    datetimes = []
    # 获取07:00-23:00时间段内的frac_Taxi
    station_row = atc_data.loc[atc_data['station_id'] == row1['nearest_station']]
    # 创建一个包含所需列名的列表
    hour_columns = [f"{i}.0" for i in range(7, 23)]

    # 使用这个列表来选取 `station_row` 中的列并进行求和
    sum_7_to_23 = station_row[hour_columns].iloc[0].sum()

    # 创建一个包含所有小时的列名的列表
    all_hour_columns = [f"{i}.0" for i in range(1, 25)]
    # 使用这个列表来选取 `station_row` 中的所有小时列并进行求和
    sum_1_to_24 = station_row[all_hour_columns].iloc[0].sum()

    # 计算 frac_taxi
    frac_taxi = station_row['frac_Taxi'] * sum_7_to_23 / sum_1_to_24
    # frac_taxi = station_row['frac_Taxi']*station_row['7.0':'23.0'].sum()/ station_row['1.0':'24.0'].sum()
    # 获取0:00-6:00时间段内的小时比例

    # 创建包含所需列名的列表
    columns = ['1.0', '2.0', '3.0', '4.0', '5.0', '6.0','23.0','24.0']

    # 使用列表选取所需的列
    selected_columns = station_row[columns].iloc[0]
    # 计算每个小时的比例
    other_hours_proportion = selected_columns.values / selected_columns.sum()

    # other_hours_proportion = station_row['1.0':'6.0'].values / station_row['1.0':'6.0'].sum()
    # 确保我们有24小时的权重
    hour_proportions = np.concatenate((other_hours_proportion, frac_taxi))
    # 根据比例生成小时数
    hours = choices(range(24), weights=hour_proportions, k=num_times)

    # 生成分钟和秒
    for hour in hours:
        minute = randint(0, 59)
        second = randint(0, 59)
        datetime_obj = datetime.now().replace(hour=hour, minute=minute, second=second, microsecond=0)
        datetimes.append(datetime_obj)

    # 按照时间先后顺序排序
    datetimes.sort()

    # 将datetime对象转换回字符串格式
    time_strings = [dt.strftime('%H:%M:%S') for dt in datetimes]

    return time_strings

if __name__ == '__main__':
    atc_flow = pd.read_csv('./atc_distribution.csv')
    atc_flow_data = pd.read_csv('./atc_flow.csv')
    print(atc_flow_data)
    print(atc_flow_data.columns)
    atc_flow_data['Cargo'] = atc_flow['Cargo']
    atc_flow_data['Private_Veh'] = atc_flow['Private_Veh']
    atc_flow_data['hour'] = atc_flow_data['Time'].str[-5:-3].astype(float)
    atc_flow_data['num_Taxi'] = atc_flow_data.apply(calculate_num_taxi, axis=1)
    atc_flow_data['num_Bus'] = atc_flow_data.apply(calculate_num_bus, axis=1)
    atc_flow_data['num_Cargo'] = atc_flow_data.apply(calculate_num_cargo, axis=1)
    atc_flow_data['num_Private_Veh'] = atc_flow_data.apply(calculate_num_priate_veh, axis=1)
    # 如果不需要hour列，可以将其删除
    atc_data = atc_flow_data.drop('hour', axis=1)

    station_list = atc_data['station_id'].unique()
    for station in station_list:
        # 选择当前station_id的所有数据
        station_index = atc_data['station_id'] == station
        # 计算当前station_id的num_Taxi总和
        num_taxi_total = atc_data.loc[station_index, 'num_Taxi'].sum()
        num_bus_total = atc_data.loc[station_index, 'num_Bus'].sum()
        num_cargo_total = atc_data.loc[station_index, 'num_Cargo'].sum()
        num_private_veh_total = atc_data.loc[station_index, 'num_Private_Veh'].sum()
        # 计算每行的frac_Taxi并直接更新原始DataFrame
        atc_data.loc[station_index, 'frac_Taxi'] = atc_data.loc[station_index, 'num_Taxi'] / num_taxi_total
        atc_data.loc[station_index, 'frac_Bus'] = atc_data.loc[station_index, 'num_Bus'] / num_bus_total
        atc_data.loc[station_index, 'frac_Cargo'] = atc_data.loc[station_index, 'num_Cargo'] / num_cargo_total
        atc_data.loc[station_index, 'frac_Private_Veh'] = atc_data.loc[station_index, 'num_Private_Veh'] / num_private_veh_total
    print(atc_data.columns)
    atc_data = atc_data.dropna()
    atc_data = atc_data[['Time', 'station_id', 'Taxi', 'Bus', 'Cargo','Private_Veh','num_Taxi', 'num_Bus', 'num_Cargo','num_Private_Veh', 'frac_Taxi',
       'frac_Bus',  'frac_Cargo',  'frac_Private_Veh',
        '1.0', '2.0', '3.0', '4.0', '5.0',
       '6.0', '7.0', '8.0', '9.0', '10.0', '11.0', '12.0', '13.0', '14.0',
       '15.0', '16.0', '17.0', '18.0', '19.0', '20.0', '21.0', '22.0', '23.0',
       '24.0', 'latitude', 'longitude']]
    atc_data.to_csv('./atc_flow.csv',index=False)
    print("Finished")
    num_times = 100  # 您需要生成的时间数量
    lat = 22.276022  # 指定的纬度
    long = 114.175147  # 指定的经度

    demand_data = pd.read_csv("./demand.csv")

    demand_data['nearest_station'] = demand_data.apply(find_nearest_station, axis=1)
    demand_data['Time'] = demand_data.apply(generate_times, axis=1)
    print(demand_data.columns)
    demand_data.to_csv('./demand_data.csv',index=False)
    # 找到最近的站点
    # nearest_station_row = find_nearest_station(lat, long, atc_data)
    # print(nearest_station_row)
    # 生成时间字符串
    # times = generate_times(num_times, nearest_station_row)
    #
    # print(f"Generated times: {times}")
    # print(f"Nearest station: {nearest_station_row['station_id']}")








    # with open('link_name.json', 'r') as handle:
    #     link_dict = json.load(handle)
    # atc_data = pd.read_csv('./atc_data.csv')
    # atc_flow = pd.read_csv('./atc_distribution.csv')
    # print(atc_data.columns)
    # atc_data = atc_data.loc[atc_data['Unnamed: 0']=='M-F']
    # atc_data.reset_index(drop=True, inplace=True)
    # atc_data = atc_data.dropna(subset=['link_coord'])
    # atc_data['link_coord'] = atc_data['link_coord'].str.replace("'", '"')
    #
    # atc_data['link_coord'] = atc_data['link_coord'].apply(json.loads)
    # atc_data['latitude'] = atc_data['link_coord'].apply(lambda x: x.get('latitude'))
    # atc_data['longitude'] = atc_data['link_coord'].apply(lambda x: x.get('longitude'))
    #
    # print(atc_data)
    #
    # columns_to_merge = [
    #     '1.0', '2.0', '3.0', '4.0', '5.0', '6.0', '7.0', '8.0',
    #     '9.0', '10.0', '11.0', '12.0', '13.0', '14.0', '15.0', '16.0', '17.0',
    #     '18.0', '19.0', '20.0', '21.0', '22.0', '23.0', '24.0', 'latitude','longitude'
    # ]
    #
    # # 添加空列到 atc_flow 以准备合并
    # for col in columns_to_merge:
    #     atc_flow[col] = np.nan
    #
    # # 对于 atc_flow 的每一行，找到 atc_data 中的匹配行并合并数据
    # for index, row in atc_flow.iterrows():
    #     # 假设 atc_flow 中的 station_id 对应于 atc_data 中的 link_id
    #     matching_row = atc_data[atc_data['link_id'] == row['station_id']]
    #     if not matching_row.empty:
    #         for col in columns_to_merge:
    #             atc_flow.at[index, col] = matching_row[col].values[0]
    #
    # # 输出合并后的结果
    # atc_flow.to_csv('./atc_flow,csv',index=False)
    # print(atc_flow)













# folder_path = './data/traffic_flow_data'
# with open('link_name.json', 'r') as handle:
#     link_dict = json.load(handle)
#
# # 使用glob模块找到所有的.xlsx文件
# file_paths = glob.glob(os.path.join(folder_path, '*.xlsx'))
#
# # 初始化一个空的列表来存储数据框
# dfs = []
#
# # 遍历文件列表，读取每个文件
# for file_path in file_paths:
# 	# 读取整个Excel文件
# 	df = pd.read_excel(file_path, engine='openpyxl')
#
# 	# 将最后一行的值设置为列名
# 	df.columns = df.iloc[-1].values  # 获取最后一行的数据作为列名
# 	df = df[:-1]  # 删除最后一行数据
#
# 	# 获取文件名（不包含扩展名）
# 	file_name = os.path.splitext(os.path.basename(file_path))[0]
#
# 	# 将文件名添加为新的一列
# 	df['link_id'] = file_name[0:4]
# 	df['link_name'] = df['link_id'].apply(lambda x: link_dict.get(str(x)))
# 	# 去掉括号及其内部的内容，包括圆括号
# 	df['link_name'] = df['link_name'].str.replace(r"\s*\(.*?\)\s*", " ", regex=True).str.strip()
# 	# 将数据框添加到列表中
# 	dfs.append(df)
#
# # 拼接所有的数据框
# concatenated_df = pd.concat(dfs, ignore_index=True)
# concatenated_df['link_coord'] = concatenated_df['link_name'].apply(find_coordinates_by_road_name)
# concatenated_df.to_csv("./atc_data.csv",index=False)
# # 打印拼接后的数据框架的内容（或进行其他处理）
# print(concatenated_df)

#
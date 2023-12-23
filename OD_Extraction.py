import pandas as pd
import numpy as np
import osmnx as ox
import random
import geopandas as gpd
from shapely.geometry import Point
from pyproj import Transformer
import networkx as nx
from random import randint, choices
from scipy.spatial.distance import cdist
from datetime import datetime
import warnings
from tqdm import tqdm
# 忽略特定类型的警告
warnings.filterwarnings("ignore", category=FutureWarning)
frac_taxi_to_cargo = 0.482
mode_count = pd.read_csv('./TCS_count.csv')  # proportions of district
num_taxi = mode_count.loc[mode_count['mode_name'] == 'Taxi', 'count'].sum()
num_tcs = mode_count.loc[mode_count['mode_name'].isin(['Bus', 'Rail', 'Taxi', 'Private Vehicle']), 'count'].sum() + num_taxi * frac_taxi_to_cargo# total num of tcs
num_total = num_tcs * 100000 / num_taxi
# hk_zone = pd.read_csv("sphk_201711.txt", sep="\t")
hk_zone = pd.read_csv("./hk_zone.csv")
atc_data = pd.read_csv('./atc_flow.csv')
geo = gpd.read_file("26PDDs.geojson")
hk_network_graph = ox.load_graphml('./data/hk_graph.graphml')
transformer_to_hk1980 = Transformer.from_crs('epsg:4326', 'epsg:2326', always_xy=True)
loc_dict = {
    'Central & Western': 'Central & Western',
    'Eastern': 'Eastern',
    'Fanling/ Sheung Shui': 'Fanling / Sheung Shui',
    'Kowloon City': 'Kowloon City',
    'Kwai Chung': 'Kwai Chung',
    'Kwun Tong': 'Kwun Tong',
    'Ma On Shan': 'Ma On Shan',
    'Mong Kok': 'Mong Kok',
    'North Lantau': 'North Lantau',
    'NENT (Other Area)': 'Rural NENT',
    'NWNT (Other Area)': 'Rural NWNT',
    'SENT (Other Area)': 'Rural SENT',
    'SWNT (Other Area)': 'Rural SWNT',
    'Sha Tin': 'Sha Tin',
    'Sham Shui Po': 'Sham Shui Po',
    'Southern': 'Southern',
    'Tai Po': 'Tai Po',
    'Tin Shui Wai': 'Tin Shui Wai',
    'Tseung Kwan O': 'Tseung Kwan O',
    'Tsing Yi': 'Tsing Yi',
    'Tsuen Wan': 'Tsuen Wan',
    'Tuen Mun': 'Tuen Mun',
    'Wan Chai': 'Wan Chai',
    'Wong Tai Sin': 'Wong Tai Sin',
    'Yau Ma Tei': 'Yau Ma Tei',
    'Yuen Long': 'Yuen Long'
}


# start_region,end_region,mode_name,count
def get_num_of_district(origin, dest):
    temp = mode_count.loc[((mode_count['start_region'] == origin) & (mode_count['end_region'] == dest)), 'count'].sum()
    num_hailing = temp / num_tcs * num_total
    return num_hailing


def get_zone(coord):
    x_proj, y_proj = transformer_to_hk1980.transform(coord.x, coord.y)
    coord = Point(x_proj, y_proj)
    for district in geo["PDD_Eng"].unique():
        polygon = geo[geo["PDD_Eng"] == district]["geometry"].iloc[0]
        if polygon.contains(coord):
            return loc_dict[district]
    return 'None'


def get_coords(district,type):
    polygon = geo[geo["PDD_Eng"]==district]["geometry"].iloc[0]
    df = pd.DataFrame()
    if type == 'origin':
        df['Coordinates'] = list(zip(hk_zone['居住地网格中心x坐标'], hk_zone['居住地网格中心y坐标']))
    else:
        df['Coordinates'] = list(zip(hk_zone['工作地网格中心x坐标'], hk_zone['工作地网格中心y坐标']))
    df['Coordinates'] = df['Coordinates'].apply(Point)

    df['In_District'] = df['Coordinates'].apply(polygon.contains)
    print(df['Coordinates'])
    in_district_df = df[df['In_District']]
    print(in_district_df)
    return in_district_df


# def get_nodes(zone, num_within_district, locate):
#     target_zone = hk_zone.loc[hk_zone[f'{locate}_district'] == zone].sample(100)
#     num_target_zone = target_zone['人数'].sum()
#     nodes_df = pd.DataFrame(columns=[f'ox_{locate}_id', f'coord_{locate}_lat', f'coord_{locate}_lng'])
#     for index, item in target_zone.iterrows():
#         num_cur_zone = int(item['人数'] / num_target_zone * num_within_district)
#         zone_coords_x = item['居住地网格中心x坐标'] if locate == 'origin' else item['工作地网格中心x坐标']
#         zone_coords_y = item['居住地网格中心y坐标'] if locate == 'origin' else item['工作地网格中心y坐标']
#
#         increase = 0.0009  # 初始增量设置为约100米
#         max_increase = 99 #0.005  # 设置最大增量边界，约500米
#         graph = None
#
#         # 尝试获取节点，如果为空，则增加搜索范围
#         while graph is None or graph.number_of_nodes() == 0 and increase <= max_increase:
#             north = zone_coords_y + increase
#             south = zone_coords_y - increase
#             east = zone_coords_x + increase
#             west = zone_coords_x - increase
#             try:
#                 # print(north, south, east, west)
#                 # graph = ox.graph_from_bbox(north, south, east, west, network_type='all')
#                 graph = ox.truncate.truncate_graph_bbox(hk_network_graph, north, south, east, west, truncate_by_edge=True)
#                 if graph is not None and graph.number_of_nodes() > 0:
#                     break
#             except (nx.NetworkXPointlessConcept,ValueError):
#                 pass
#             increase += 0.0009  # 增加搜索范围
#         print("="*5,round(len(nodes_df)/num_within_district*100,2),'%',"="*5)
#         # 如果最终找到节点
#         if graph is not None and graph.number_of_nodes() > 0:
#             all_nodes = list(graph.nodes)
#             selected_nodes = np.random.choice(all_nodes, size=num_cur_zone, replace=True).tolist()
#             for node_id in selected_nodes:
#                 node = graph.nodes[node_id]
#                 nodes_df = nodes_df.append({f'ox_{locate}_id': node_id, f'coord_{locate}_lat': node['y'], f'coord_{locate}_lng': node['x']}, ignore_index=True)
#         else:
#             print(f"No nodes found for zone {zone} even after expanding the search area.")
#             continue  # 如果即使增加到最大范围还是找不到节点，就跳过这个区域
#     print(num_within_district,len(nodes_df))
#     return nodes_df

all_nodes_dict = {}
def get_nodes(zone, num_within_district, locate):
    global all_nodes_dict
    target_zone = hk_zone.loc[hk_zone[f'{locate}_district'] == zone]
    num_target_zone = target_zone['人数'].sum()
    nodes_df = pd.DataFrame(columns=[f'ox_{locate}_id', f'coord_{locate}_lat', f'coord_{locate}_lng'])

    for index, item in tqdm(target_zone.iterrows(), total=target_zone.shape[0]):
        num_cur_zone = int(item['人数'] / num_target_zone * num_within_district)
        zone_coords = (item['居住地网格中心x坐标'], item['居住地网格中心y坐标']) if locate == 'origin' else (
        item['工作地网格中心x坐标'], item['工作地网格中心y坐标'])
        # 检查是否已缓存了区域节点
        if zone_coords in all_nodes_dict:
            graph = all_nodes_dict[zone_coords]
            if graph is not None:
                all_nodes = list(graph.nodes)
            else:
                all_nodes = None
        else:
            # 如果没有缓存，则执行搜索并将结果添加到字典中
            all_nodes, graph = find_nodes(zone_coords)
            all_nodes_dict[zone_coords] = graph
        # 现在 all_nodes 包含了缓存的节点或新搜索到的节点
        # print("=" * 5, round(len(nodes_df) / num_within_district * 100, 2), '%', "=" * 5)

        if all_nodes is not None:
            selected_nodes = np.random.choice(all_nodes, size=num_cur_zone, replace=True).tolist()
            for node_id in selected_nodes:
                node = graph.nodes[node_id]
                nodes_df = nodes_df.append({
                    f'ox_{locate}_id': node_id,
                    f'coord_{locate}_lat': node['y'],
                    f'coord_{locate}_lng': node['x']
                }, ignore_index=True)
        else:
            print(f"No nodes found for zone {zone} even after expanding the search area.")
            continue
    return nodes_df


def find_nodes(zone_coords, initial_increase=0.0009, max_increase=0.005):
    increase = initial_increase
    graph = None
    all_nodes = None

    while increase <= max_increase:
        north = zone_coords[1] + increase
        south = zone_coords[1] - increase
        east = zone_coords[0] + increase
        west = zone_coords[0] - increase

        # 尝试从缓存的图中截取区域
        try:
            graph = ox.truncate.truncate_graph_bbox(hk_network_graph, north, south, east, west, truncate_by_edge=True)
        except (nx.NetworkXPointlessConcept, ValueError):
            pass  # 如果截取失败，忽略异常

        # 检查是否有节点
        if graph is not None and graph.number_of_nodes() > 0:
            all_nodes = list(graph.nodes)
            break

        # 如果截取的图中没有节点，则尝试从在线数据获取
        if graph is None or graph.number_of_nodes() == 0:
            try:
                graph = ox.graph_from_bbox(north, south, east, west, network_type='all')
                if graph.number_of_nodes() > 0:
                    all_nodes = list(graph.nodes)
                    break
            except (nx.NetworkXPointlessConcept, ValueError):
                pass  # 如果在线获取失败，忽略异常

        increase += initial_increase  # 增加搜索范围
    return all_nodes, graph

def generate_list(num,ratio_dict):
    ratio_list = list(ratio_dict.values())
    type_list = list(ratio_dict.keys())

    distribution = []
    for i in range(int(num)):
        distribution.append(random.choices(type_list, weights=ratio_list)[0])

    return distribution


def get_proportion(origin,dest,propotion_taxi=frac_taxi_to_cargo):
    result_dict = {'Bus':0,'Taxi':0,'Rail':0,'Private Vehicle':0,'Cargo':0}
    mode_list = ['Bus','Taxi','Rail','Private Vehicle']
    mode_sum = mode_count.loc[((mode_count['start_region'] == origin) & (mode_count['end_region'] == dest)&(mode_count['mode_name'].isin(['Bus', 'Rail', 'Taxi','Private Vehicle']))), 'count'].sum()
    for mode in mode_list:
        result_dict[mode] += mode_count.loc[((mode_count['start_region'] == origin) & (mode_count['end_region'] == dest)&(mode_count['mode_name'] == mode)), 'count'].sum()/mode_sum
    result_dict['Cargo'] = result_dict['Taxi']*propotion_taxi
    return result_dict


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


def generate_times(row1, num_times=1):
    datetimes = []
    mode_ = row1['mode']
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
    if mode_ == 'Taxi':
        # 计算 frac_taxi
        frac_mode = station_row['frac_Taxi'] * sum_7_to_23 / sum_1_to_24
    elif mode_ == 'Bus':
        # 计算 frac_taxi
        frac_mode = station_row['frac_Bus'] * sum_7_to_23 / sum_1_to_24
    elif mode_ == 'Cargo':
        # 计算 frac_taxi
        frac_mode = station_row['frac_Cargo'] * sum_7_to_23 / sum_1_to_24
    elif mode_ == 'Private Vehicle':
        frac_mode = station_row['frac_Private_Veh'] * sum_7_to_23 / sum_1_to_24
    else:
        frac_mode = station_row['frac_Taxi'] * sum_7_to_23 / sum_1_to_24
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
    hour_proportions = np.concatenate((other_hours_proportion, frac_mode))
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

    return time_strings[0]


if __name__ == '__main__':
    # Get total num of hailing
    demand_data = pd.DataFrame(columns=['Time','mode','origin_ox_id','origin_coord_lat','origin_coord_lng','origin_district','dest_ox_id','dest_coord_lat','dest_coord_lng','dest_district'])
    result_df = pd.DataFrame()
    # Spatial distribution of data --> TCS + HK
    # Distribution among districts
    origin_loc_list = mode_count['start_region'].unique()
    for origin_loc in origin_loc_list:
        dest_loc_list = mode_count.loc[mode_count['start_region'] == origin_loc,'end_region'].unique()
        for dest_loc in dest_loc_list:
            district_df = pd.DataFrame()
            num_district = get_num_of_district(origin_loc,dest_loc)
            print(origin_loc,dest_loc)
            nodes_start_df = get_nodes(origin_loc, num_district, 'origin')
            nodes_dest_df = get_nodes(dest_loc,num_district,'dest')
            nodes_df = pd.concat([nodes_start_df, nodes_dest_df], axis=1)
            nodes_df = nodes_df.dropna()
            district_df['origin_ox_id'] = nodes_df['ox_origin_id'].values
            district_df['origin_coord_lat'] = nodes_df['coord_origin_lat'].values
            district_df['origin_coord_lng'] = nodes_df['coord_origin_lng'].values
            district_df['dest_ox_id'] = nodes_df['ox_dest_id'].values
            district_df['dest_coord_lat'] = nodes_df['coord_dest_lat'].values
            district_df['dest_coord_lng'] = nodes_df['coord_dest_lng'].values
            district_df['origin_district'] = origin_loc
            district_df['dest_district'] = dest_loc
            district_df['nearest_station'] = district_df.apply(find_nearest_station, axis=1)
            mode_proportion = get_proportion(origin_loc,dest_loc)
            mode_proportion_list = generate_list(len(district_df), mode_proportion)
            district_df['mode'] = mode_proportion_list
            district_df['Time'] = district_df.apply(generate_times, axis=1)
            order_list = ['Time','mode','origin_ox_id', 'origin_coord_lat', 'origin_coord_lng', 'dest_ox_id',
                   'dest_coord_lat', 'dest_coord_lng',   'origin_district',
                   'dest_district', 'nearest_station']
            district_df = district_df[order_list]

            district_df['Time'] = pd.to_datetime(district_df['Time'], format='%H:%M:%S').dt.time

            # 根据时间排序
            district_df = district_df.sort_values(by='Time')

            result_df = result_df.append(district_df,ignore_index=True)
            result_df.to_csv('./demand.csv',index=False)


    # Temporal distribution of data --> ATC


import requests
import json
import pandas as pd
# 假设这是API的URL
url = "https://rt.data.gov.hk/v2/transport/citybus/eta/CTB/001145/11"
url_company = "https://rt.data.gov.hk/v2/transport/citybus/company/CTB"
url_route = "https://rt.data.gov.hk/v2/transport/citybus/route/CTB"
# 发起GET请求
kwloon_url = "https://data.etabus.gov.hk/v1/transport/kmb/route-stop/"
nlb_url = "https://rt.data.gov.hk/v2/transport/nlb/route.php?action=list"

if __name__ == '__main__':
    with open('./data/kmb_route_list.json', 'r', encoding='utf-8') as f:
        route_data = json.load(f)
    route_df = pd.DataFrame(route_data['data'])
    print(route_df)
    route_list = route_df['route'].unique()
    print(route_list)
    citybus_list = ['20','20A','22','22D','22M','22X','701','701A','701S','702','702A','702B','702S','N20','20R','20S','22R']
    route_numbers = [
        "1", "1A", "2", "2A", "2B", "2D", "2E", "2F", "2P", "2X", "3B", "3C", "3D", "3M",
        "3X", "5", "5A", "5C", "5D", "5M", "5P", "5R", "5X", "6", "6C", "6D", "6F", "6P",
        "6X", "7", "7B", "7M", "8", "8A", "8P", "9", "10", "11", "11B", "11C", "11D", "11K",
        "11X", "12", "12A", "12P", "13D", "13M", "13P", "13X", "14", "14B", "14D", "14H",
        "14X", "15", "15A", "15X", "16", "16M", "16P", "16X", "17", "18", "23", "23M", "24",
        "26", "26M", "26X", "27", "28", "28B", "28S", "29M", "203C", "203E", "203S", "208",
        "211", "211A", "213A", "213B", "213D", "213M", "213S", "213X", "214", "214P", "215P",
        "215X", "216M", "219X", "224X", "N3D", "N213", "N214", "N216", "W2", "W4", "X6C",
        "3S", "6R", "25R", "215R", "216R", "224R", "225R", "R215"
    ]
    print(len(route_numbers))
    kwloon_df = route_df.loc[route_df['route'].isin(route_numbers)]
    print(kwloon_df)
    kwloon_df = kwloon_df.drop_duplicates(subset='route')
    kwloon_df['co'] = 'KMB'
    kwloon_df.to_csv("./kmb_kwloon.csv",index=False)
    # inbound_list = []
    # outbound_list = []
    # all_data = []
    # for route in route_list:
    #     url_stop = f"https://rt.data.gov.hk/v2/transport/nlb/route.php?action=list&routeId={route}"
    #     response = requests.get(url_stop)
    #     if response.status_code == 200:
    #         # 请求成功
    #         print("请求成功: ", response.status_code)
    #         data = response.json()
    #         all_data.append(data)  # 将数据添加到列表中
    #     else:
    #         print("请求失败: ", response.status_code)
    #
    #         # 将所有数据保存为JSON文件
    # with open('./data/all_routes_data.json', 'w', encoding='utf-8') as f:
    #     json.dump(all_data, f, ensure_ascii=False, indent=4)
    # for route in route_data['data']:
    #     print(route)
    # # 检查响应状态码
    # response = requests.get(nlb_url)
    # if response.status_code == 200:
    #     # 请求成功
    #     print("请求成功: ", response.status_code)
    #     # 处理响应数据
    #     data = response.json()
    #     with open('./data/route_stop.json', 'w', encoding='utf-8') as f:
    #         json.dump(data, f, ensure_ascii=False, indent=4)
    #     print(data)
    # else:
    #     # 请求失败
    #     print("请求失败: ", response.status_code)
    #     print("失败信息: ", response.text)

# 注意: 许多API有调用频率限制，确保不要过于频繁地调用API
import time
import requests
import os
import sys
import getpass
import json
from pykml import parser
import math
import random

base_address = "http://localhost:8000/"
camera = "arcgisearth/camera"
snapshot = "arcgisearth/snapshot"
addgraphic = "arcgisearth/graphics"


def get_camera():
    url = base_address + camera
    r = requests.get(url, verify=False)
    print(r.content)
    return r.content


def reverse_geocoding(coordinate):
    lon = coordinate[0]
    lat = coordinate[1]
    url = f'https://nominatim.openstreetmap.org/reverse.php?lat={lat}&lon={lon}&zoom=18&format=jsonv2'
    resp = requests.get(url)
    # resp_dict = resp.json()
    # country = resp_dict.get('address').get('country')
    # state = resp_dict.get('address').get('state')
    # city = resp_dict.get('address').get('city')
    display = resp.json().get('display_name')
    # print('Country: ' + country + '\n' + 'Province: ' + state + '\n' + 'City: ' + city + '\n')
    return display
    print(display)


def open_file(region):  # read KML file
    file_name = region + '.kml'
    with open(f'region\\{file_name}', 'r') as f:
        kml = parser.parse(f).getroot()
        coordinates = str(kml.Placemark.Polygon.outerBoundaryIs.LinearRing.coordinates)
        coordinates = coordinates.replace('\n', '').split(sep=' ')
        coordinates = [i for i in coordinates if i != '']
        coordinates = [i for i in coordinates if i != '\n']  # 这个时候是个把初始字符串转换的列表

        coordinates_array_original = []
        for i in coordinates:
            i = tuple(eval(i))
            coordinates_array_original.append(i)  # 以数组嵌套元组形式存储三维坐标

        coordinates_array = []
        for i in coordinates_array_original:
            tup = (i[0], i[1])
            coordinates_array.append(tup)  # 取出三维坐标的前2维度，也就是经度和维度存进去

        return coordinates_array
        # print('成功提取多边形坐标:' + str(coordinates_array))


def whether_point_within(point, region):  # 传入一个元组形式的需要被判定的点，如果符合则返回True，region不需要已读，可以在此执行读取
    coordinates_array = open_file(region)
    # 这里先对点是否处于多边形经度范围内做一个判断（这里是针对球面坐标系是一个循环体的修正）
    left_point, right_point = get_furthest_points(coordinates_array)
    lon_positive = max(left_point[0], right_point[0])
    lon_negative = min(left_point[0], right_point[0])
    lon_difference = abs(left_point[0] - right_point[0])  # 最关键的一个思路：通过求差值的绝对值，来判断多边形的内部在哪边
    if lon_difference < 180:
        if lon_negative < point[0] < lon_positive:
            lon_within = True
        else:
            lon_within = False
    else:
        if lon_negative < point[0] < lon_positive:
            lon_within = False
        else:
            lon_within = True

    # 如通过上述判断，会执行下面的精细判断；没通过直接返回False
    if lon_within:
        length = len(coordinates_array)
        intersect = 0
        for i in range(length-1):
            if i == length - 1:
                line = [coordinates_array[i], coordinates_array[0]]
            else:
                line = [coordinates_array[i], coordinates_array[i + 1]]

            point_on_line = point_on_line_with_same_lat(line, point)  # 计算下取出的第一条线段是否能在该纬度获取交点
            if not point_on_line:
                continue  # 无交点，继续
            else:
                if calculate_point_distance(point, point_on_line):
                    intersect = intersect + 1
                else:
                    continue
        if intersect % 2 != 0:
            return True
        else:
            return False
    else:
        return False


def get_furthest_points(array):  # 找出组成多边形的array中经度距离最远的两个点
    length = len(array)
    max_difference = 0
    for i in range(length-1):
        for j in range(length-1):
            difference = abs(array[i][0] - array[j][0])
            if difference > max_difference:
                max_difference = difference
                i_max = i
                j_max = j
            else:
                continue
    return array[i_max], array[j_max]

# def calculate_angle(point1, point2):  # 算出来的是与0度经线的夹角，逆时针时为正
#     dx = point2[0] - point1[0]
#     dy = point2[1] - point1[1]
#     if dx == 0:
#         if dy > 0:
#             return 90
#         else:
#             return 270
#     else:
#         angle = math.atan(dy / dx) / math.pi * 180
#         if dx > 0:
#             return angle
#         if dx < 0 and dy > 0:
#             return angle + 180
#         if dx < 0 and dy < 0:
#             return angle - 180
# 这部分算法因为角度的计算精度问题，失效了


def reverse(a):  # 把点翻转变成以90°经线为对称轴的对称点，主要应用于把当前两点翻转成子午线航线
    if a > 0:
        b = (a - 180) * (-1)
    else:
        b = (a + 180) * (-1)
    return b


def point_on_line_with_same_lat(line, point):  # 计算line上与point拥有同样纬度的交点。line：数组嵌套元组。point：元组
    if (line[0][1] > point[1] > line[1][1]) or (line[0][1] < point[1] < line[1][1]):
        result_point_lat = point[1]

        ratio = abs((point[1] - line[0][1]) / (line[1][1] - line[0][1]))  # 求的是【point与点1的距离】与【点1点2距离】之比
        lon_meridian_difference = line[1][0] - line[0][0]  # 线上点2-点1的过本初子午线经度之差
        result_point_lon = lon_meridian_difference * ratio + line[0][0]

        # lon_product = line[0][0] * line[1][0]
        lon_difference = abs(line[0][0]) + abs(line[1][0])

        if lon_difference > 180:  # 当两个点经度之差绝对值大于180，这两点要走对侧子午线航线
            reverse_point1_lon = reverse(line[0][0])
            reverse_point2_lon = reverse(line[1][0])
            result_point_lon = reverse((reverse_point2_lon - reverse_point1_lon) * ratio + reverse_point1_lon)

        result_point = (result_point_lon, result_point_lat)
        return result_point
    else:
        return False  # 点的纬度超出线的纬度


def calculate_point_distance(start_point, end_point, distance_range=180):  # 计算起始点向右发射180度射线，是否能经过结束点，是则返回True
    start = start_point[0]
    end = end_point[0]
    if end > start:
        if end - start < distance_range:
            return True
        else:
            return False
    else:
        if start - end > 360 - distance_range:
            return True
        else:
            return False


def generate_random_point():
    x = (random.random() * 360) - 180
    y = (random.random() * 180) - 90
    random_point = (x, y)
    return random_point


def random_location_patch(point, id):
    location = f'''
        {{
            "id": "{id}",
            "geometry": {{
                "type": "point",
                "x": {point[0]},
                "y": {point[1]}
            }},
            "symbol": {{
                "type": "picture-marker",
                "url": "https://static.arcgis.com/images/Symbols/Shapes/BlackStarLargeB.png",
                "width": "20px",
                "height": "20px",
                "angle":0,
                "xoffset": "0px",
                "yoffset": "0px"
            }}
        }}
        '''
    url = base_address + addgraphic
    headers = {'content-Type': 'application/json'}
    r = requests.post(url, data=location, headers=headers, verify=False)


def remove_graphic(number=10000):  # 给出一个你想移除的编号范围
    for i in range(number):
        url_remove = base_address + addgraphic + f'/{i}'
        r = requests.delete(url_remove).status_code
        if r == 204:
            print('编号为' + str(i) + '成功移除')
        else:
            print('编号为' + str(i) + '移除失败，可能因为不存在此编号')


def check_your_algorithm(volume):
    for i in range(volume):
        point = generate_random_point()

        within = whether_point_within(point, 'Africa')
        if within:
            random_location_patch(point, i)
        else:
            continue


if __name__ == '__main__':
    # check_your_algorithm(10000)
    remove_graphic(10000)

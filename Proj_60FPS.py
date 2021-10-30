import time
import requests
import os
import sys
import getpass
import json

base_address = "http://localhost:8000/"
camera = "arcgisearth/camera"
snapshot = "arcgisearth/snapshot"


def mkdir(path):
    path = path.strip()
    path = path.rstrip("\\")
    exist = os.path.exists(path)
    if not exist:
        os.makedirs(path)
    else:
        return


def get_camera():
    url = base_address + camera
    r = requests.get(url, verify=False)
    return r.content


def set_camera(coords):  # 格式化set_camera的参数，传入的coord需要包含
    url = base_address + camera
    location_temp = f'''
    {{
        "position": {{
            "x": {coords[0]},
            "y": {coords[1]},
            "z": {coords[2]},
            "spatialReference": {{
                "wkid": 4326
            }}
        }},
        "heading": 359.9587533944618,
        "tilt": 5.176166585626318e-16,
        "roll": 0
    }}
    '''

    headers = {'content-Type': 'application/json'}
    r = requests.put(url, location_temp, headers=headers, verify=False)


def get_snapshot():
    url = base_address + snapshot
    r = requests.get(url, stream=True, verify=False)
    filename = f'{i}_【{z}】,{x},{y}'
    print(filename)
    path = f"{mkdirpath}\\{filename}.jpg"
    with open(path, 'wb') as f:
        for chunk in r:
            f.write(chunk)


def reverse_geocoding(coordinate):  # 把coordinate坐标逆地理编码，并生成报告
    lon = coordinate[0]
    lat = coordinate[1]
    url = f'https://nominatim.openstreetmap.org/reverse.php?lat={lat}&lon={lon}&zoom=18&format=jsonv2'
    resp = requests.get(url)

    display = str(resp.json().get('display_name'))
    if display == 'None':
        display = 'This location is hidden within the ocean.'
    report = ['The address of the address is...\n\n', display, '\n\n',
              '\n\n-----------------------------------\nDesigned and Created by SHELBERT',
              '\n-----------------------------------']
    with open(f"{mkdirpath}\\Report.txt", 'w', encoding='utf-8') as f:
        f.writelines(report)


def check_setting():  # 检查本地设置是否已经打开Automation API权限
    username = getpass.getuser()
    print('Got username')
    with open(f'C:\\Users\\{username}\\Documents\\ArcGISEarth\\automation\\settings.json', 'r') as f:
        print('File Opened')
        data = json.load(f)
        print('Loaded json into dict')
        if data['autoStart']:
            print('autoStart is True, proceed')
            return
        else:
            data['autoStart'] = True
            print('Modified autoStart')
    with open(f'C:\\Users\\{username}\\Documents\\ArcGISEarth\\automation\\settings.json', 'w') as r:
        json.dump(data, r)
        print('New data written')
    print('Successfully updated the Auto-API settings, proceed.')
    # sys.exit(0)


def generate_Height(number, max_height=70000, min_height=1000):  # 拍下number数量的照片，首尾包含max与min高度
    height_list = []
    difference = max_height - min_height
    interval = difference/(number-1)
    int(interval)
    pic_num = 0
    height = max_height
    height_list.append(height)
    while pic_num < number-2:
        pic_num = pic_num + 1
        height = height - interval
        height_list.append(height)
    height_list.append(min_height)
    return height_list


if __name__ == '__main__':
    try:
        check_setting()
    except:
        print('CheckSetting failed')
        time.sleep(20)

    mkdirpath = 'K:\\Media\\VideoClips\\20210526Proj_60FPS\\DifferentFrame\\10FPS'
    mkdir(mkdirpath)
    location = get_camera()
    lodict = eval(location)  # 这个字典是用来给location参数传值的，因为set_camera函数只能接受特定格式的数据

    x = lodict['position']['x']
    y = lodict['position']['y']
    z = lodict['position']['z']

    lodict['position']['x'] = x
    lodict['position']['y'] = y

    current_coordinate = (x, y)
    reverse_geocoding(current_coordinate)

    z_list = generate_Height(100, 6000000, 5000)
    print(z_list)
    print(len(z_list))

    i = 0
    for z in z_list:
        i = i + 1
        location = str(lodict)
        print('打印中' + location)
        x = 84.95
        y = 30.75
        coords = (x, y, z)
        set_camera(coords)
        time.sleep(5)
        get_snapshot()

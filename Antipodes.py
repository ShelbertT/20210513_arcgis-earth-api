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
    # print(r.content)
    return r.content


def set_camera(location):
    url = base_address + camera
    # print(url)
    headers = {'content-Type': 'application/json'}
    r = requests.put(url, location, headers=headers, verify=False)


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
    report = ['The address of the antipode is...\n\n', display, '\n\nHere, any step ahead is a step home.',
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


if __name__ == '__main__':
    try:
        check_setting()
    except:
        print('CheckSetting failed')
        time.sleep(20)

    mkdirpath = 'C:\\Antipode'
    mkdir(mkdirpath)
    location = get_camera()

    lodict = eval(location)  # 这个字典是用来给location参数传值的，因为set_camera函数只能接受特定格式的数据
    x = lodict['position']['x']
    y = lodict['position']['y']
    z = lodict['position']['z']

    if x > 0:
        x = x - 180
    else:
        x = x + 180
    y = -y

    lodict['position']['x'] = x
    lodict['position']['y'] = y  # 把翻转后的坐标更新进字典

    current_coordinate = (x, y)
    reverse_geocoding(current_coordinate)
    i = 0
    for z in (
    10000000, 7500000, 5000000, 2500000, 1000000, 750000, 500000, 200000, 150000, 100000, 50000, 30000, 20000, 10000,
    5000):
        i = i + 1
        lodict['position']['z'] = z
        location = str(lodict)
        print('打印中' + location)
        set_camera(location)
        time.sleep(20)
        get_snapshot()

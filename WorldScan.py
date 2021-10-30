import random
import time
import requests
import os
import sys
import getpass
import json
import cv2
import readkml

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


def location_format(x_temp, y_temp, z_temp=50000):  # 根据传值xy生成格式化string
    location = f'''
    {{
        "position": {{
            "x": {x_temp},
            "y": {y_temp},
            "z": {z_temp},
            "spatialReference": {{
                "wkid": 4326
            }}
        }},
        "heading": 0,
        "tilt": 0,
        "roll": 0
    }}
    '''
    return location.strip('\n')


def set_camera(location_temp):  # 按照格式标准location放置相机
    url = base_address + camera
    headers = {'content-Type': 'application/json'}
    r = requests.put(url, location_temp, headers=headers, verify=False)


def get_camera():
    url = base_address + camera
    r = requests.get(url, verify=False)
    print(r.content)
    return r.content


def get_snapshot():
    url = base_address + snapshot
    r = requests.get(url, stream=True, verify=False)
    filename = f'{photo_number}_{x},{y}'
    print(filename)
    path = f"{mkdirpath}\\{filename}.jpg"
    with open(path, 'wb') as f:
        for chunk in r:
            f.write(chunk)


def check_earth():
    try:
        set_camera()
        return
    except:
        print('Please install and run ArcGIS Earth first! You can download it from here:')
        print('https://www.esri.com/en-us/arcgis/products/arcgis-earth/overview')
        time.sleep(20)
        sys.exit(0)


def check_settings():
    username = getpass.getuser()
    with open(f'C:\\Users\\{username}\\Documents\\ArcGISEarth\\automation\\settings.json', 'r') as f:
        data = json.load(f)
        if data['autoStart']:
            return
        else:
            data['autoStart'] = True
    with open(f'C:\\Users\\{username}\\Documents\\ArcGISEarth\\automation\\settings.json', 'w') as r:
        json.dump(data, r)
    print('Successfully updated the Auto-API settings, please restart ArcGIS Earth and this program.')
    time.sleep(20)
    sys.exit(0)


def manual_snapshot():
    mkdirpath = f'C:\\What_a_Wonderful_World\\manual'
    mkdir(mkdirpath)

    camera_raw = get_camera()
    camera_dict = json.loads(camera_raw)
    print(camera_dict)
    global x
    x = camera_dict['position']['x']
    global y
    y = camera_dict['position']['y']
    location = location_format()
    url = base_address + camera
    headers = {'content-Type': 'application/json'}
    r = requests.put(url, location, headers=headers, verify=False)
    time.sleep(10)
    get_snapshot()


if __name__ == '__main__':
    region = 'China'
    mkdirpath = 'F:\\Database\\ChinaScan\\2'
    mkdir(mkdirpath)
    photo_number = 0

    point_list = readkml.generate_web_within_polygon(region)
    for point in point_list:
        x = point[0]
        y = point[1]
        location = location_format(x, y)
        set_camera(location)
        time.sleep(15)
        photo_number += 1
        get_snapshot()




    # location = location_format()


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


def random_location():
    global x  # 这里使用全局变量是为了方便写入文件名
    x = (random.random() * 360) - 180  # 经度
    global y
    y = (random.random() * 180) - 90
    while not readkml.whether_point_within((x, y), region):  # 如果(x, y)不在限定区域内，它就会继续刷点，直到刷出来在里面的
        x = (random.random() * 360) - 180
        y = (random.random() * 180) - 90
    location_format_content = location_format()
    return location_format_content


def location_format():
    location = f'''
    {{
        "position": {{
            "x": {x},
            "y": {y},
            "z": 8000,
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


def set_camera():
    location = random_location()
    url = base_address + camera
    # print(url)
    headers = {'content-Type': 'application/json'}
    r = requests.put(url, location, headers=headers, verify=False)


def get_camera():
    url = base_address + camera
    r = requests.get(url, verify=False)
    print(r.content)
    return r.content


def get_snapshot():
    url = base_address + snapshot
    r = requests.get(url, stream=True, verify=False)
    filename = f'{x},{y}'
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
    region = 'Africa'

    check_settings()
    check_earth()  # 运行前检查

    i = 1
    mkdirpath = f'C:\\What_a_Wonderful_World\\{region}'
    mkdir(mkdirpath)
    print(
        '\n' + '\n' + '------------------------------' + '\n' + 'What\'s life without whimsy?' + '\n' + '------------------------------' + '\n' + '\n' + '\n')
    print('Initiating......Files are stored in this location:' + '\n' + mkdirpath)
    time.sleep(5)
    while i < 1000:
        print('\n' + 'Teleporting to the next location... No.' + str(i))
        set_camera()
        time.sleep(20)
        get_snapshot()
        i = i + 1

    # mkdirpath = f'C:\\What_a_Wonderful_World\\manual'
    # mkdir(mkdirpath)
    # manual_snapshot()



# driver = webdriver.Chrome()
# driver.get("http://localhost:8000/sample/index.html")
#
# driver.find_element_by_xpath('//*[@id="apisPanel"]/div[2]/div').click()
# driver.find_element_by_id("inputArea").send_keys(location)
# driver.find_element_by_xpath('//*[@id="apiArgs"]/div/button[2]').click()
#
# time.sleep(3)
#
# driver.find_element_by_xpath('//*[@id="apisPanel"]/div[15]/div').click()
# driver.find_element_by_xpath('//*[@id="btnDiv"]').click()
#
# url = driver.find_element_by_xpath('//*[@id="respImg"]').get_attribute('src')
# driver.quit()
#
# r = requests.get(url)
#
# with open('test', 'wb') as f:
#     f.write(r.content)

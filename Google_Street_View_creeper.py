"""
_*_ coding: utf-8 _*_
__author__ = 'Zihang'
__date__   = '2023_03_23'
"""

import urllib.request as ur
import urllib
import os
from tqdm import tqdm


def download(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/88.0.4324.150 Safari/537.36 Edg/88.0.705.68'}
    header = ur.Request(url, headers=headers)
    err = 0
    while err < 3:
        try:
            data = ur.urlopen(header).read()
        except:
            err += 1
        else:
            return data
    raise Exception("Bad network link.")


def recu_down(url, filename):  # recurrent download with ContentTooShortError
    try:
        urllib.request.urlretrieve(url, filename)
    except urllib.error.ContentTooShortError:
        print('Network conditions is not good. Reloading...')
        recu_down(url, filename)


# Your study area
leftTop = [77, 28]  # Lon Lat
rightBottom = [77, 28]
width = 11111
height = 22222

stepLon = (rightBottom[0] - leftTop[0]) / width
stepLat = (rightBottom[1] - leftTop[1]) / height

cols = width // 224  # patch size is 224
rows = height // 224
curX = leftTop[0] + stepLon * 111
curY = leftTop[1] + stepLat * 111

# 根据遥感patch的i, j去选街景的Lon, Lat
path = 'your/path/to/patch/data'
file_list = os.listdir(path)
print(len(file_list))

for k in tqdm(range(0, len(file_list))):
    i = int(file_list[k].split('_')[2])
    j = int(file_list[k].split('_')[3][:-4])  # -4是.png
    FID = i * cols + j
    X = curX + 224 * j * stepLon
    Y = curY + 224 * i * stepLat
    print(Y, X)

    Your_Key = 'Your_Key'
    # 爬取元数据，查看是否符合要求
    url_ = 'https://maps.googleapis.com/maps/api/streetview/metadata?location=' + str(Y) + ',' + \
           str(X) + Your_Key

    img_meta = download(url_)
    img_meta = img_meta.decode()  # decode
    img_meta_lists = img_meta.splitlines()  # 按行划分字符串
    print(k, img_meta_lists)

    # 先查看元数据，可用就下载影像素
    # 年份对应的日期是[2]13到17, pano的有效字符[7]16到-2
    if len(img_meta_lists[2]) >= 5:
        img_meta_year_line = img_meta_lists[2]
        print(img_meta_year_line)
        img_meta_year = int(img_meta_year_line[13:17])
        print('year: ',img_meta_year)
        if img_meta_year == 2022 or img_meta_year == 2023 or img_meta_year == 2021:
            img_meta_pano_line = img_meta_lists[8]
            print('pano_line: ',img_meta_pano_line)
            img_meta_pano = img_meta_pano_line[16:-2]
            print('pano: ', img_meta_pano)
            for direction in range(4):  # 下载四个角度的街景
                heading = 90 * direction
                img_src = 'https://maps.googleapis.com/maps/api/streetview?size=1024x1024&pano=' + img_meta_pano + \
                          '&heading=' + str(heading) + '&pitch=0&' + Your_Key
                recu_down(img_src, 'your/path/to/save/streetview' + str(FID) + '_' +
                          str(i) + '_' + str(j) + '_' + str(direction + 1) + '.jpg')

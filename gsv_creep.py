"""
_*_ coding: utf-8 _*_
__author__ = 'Zihang'
__date__   = '2023_03_23'
"""

import requests
import random
import urllib.request as ur
import urllib
import json
import cv2

import os
from tqdm import tqdm
import pandas as pd
import numpy as np
import re
import math


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


# # mumbai参数
# leftTop = [72.84195902139877, 19.10073817777462]
# rightBottom = [72.91544724724137, 18.98959156366031]
# width = 16601
# height = 26562

# faridabad
leftTop = [77.255859375, 28.5589599609]
rightBottom = [77.3863220215, 28.2939147949]
width = 24320
height = 49408

stepLon = (rightBottom[0] - leftTop[0]) / width
stepLat = (rightBottom[1] - leftTop[1]) / height

cols = width // 224
rows = height // 224
curX = leftTop[0] + stepLon * 111
curY = leftTop[1] + stepLat * 111

# # 失败重新爬取时获得上次爬取的最后一个文件的ID
# patch_center = pd.read_csv('./mumbai_2021_patch_center.csv')
# path = r'D:\Codes\Python\RSE\00X_creep\gsv_all_patch'
# file_list = os.listdir(path)
# file_list.sort(key=lambda x: int(x.split('_')[1]))  # 重新按数字大小排序
# pause_ID = file_list[-1].split('_')[1] # 获取中断前最后一个ID
# print(pause_ID)

# 根据遥感patch的i, j去选街景的Lon, Lat
path = '../data_patch/faridabad_2022'
file_list = os.listdir(path)
print(len(file_list))

for k in tqdm(range(0, len(file_list))):
    i = int(file_list[k].split('_')[2])
    j = int(file_list[k].split('_')[3][:-4])  # -4是.png
    FID = i * cols + j
    X = curX + 224 * j * stepLon
    Y = curY + 224 * i * stepLat
    print(Y,X)

    # 爬取元数据，查看是否符合要求
    url_ = 'https://maps.googleapis.com/maps/api/streetview/metadata?location=' + str(Y) + ',' + \
           str(X) + '&key=AIzaSyBCuWS9yGVAmd1909kcM3W9qGappuQvvPw'
    img_meta = download(url_)
    img_meta = img_meta.decode()
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
            print('pano: ',img_meta_pano)
            for direction in range(4):  # 下载四个角度的街景
                heading = 90 * direction
                img_src = 'https://maps.googleapis.com/maps/api/streetview?size=1024x1024&pano=' + img_meta_pano + \
                          '&heading=' + str(heading) + '&pitch=0&key=AIzaSyBCuWS9yGVAmd1909kcM3W9qGappuQvvPw'
                recu_down(img_src, './faridabad/streetimg_' + str(FID) + '_' +
                          str(i) + '_' + str(j) + '_' + str(direction + 1) + '.jpg')

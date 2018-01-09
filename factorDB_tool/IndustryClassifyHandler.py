#!/usr/bin/env/ python3
# -*- coding: utf-8 -*-
# @Abstract: 导入股票行业分类数据
# @Filename: IndustryClassifyHandler
# @Date:   : 2018-01-09 03:32
# @Author  : YuJun
# @Email   : yujun_mail@163.com

from configparser import ConfigParser
import os
import csv
import pandas as pd


def load_industry_classify(standard='sw'):
    """导入个股行业分类数据"""
    cfg = ConfigParser()
    cfg.read('config.ini')
    # 读取申万一级行业信息
    sw_classify_info_path = os.path.join(cfg.get('industry_classify', 'classify_data_path'), 'classify_standard_sw.csv')
    df_sw_classify = pd.read_csv(sw_classify_info_path, names=['ind_code', 'ind_name'], header=0)
    # 读取股票最新行业分类原始数据，导入本系统的股票申万一级行业分类数据文件
    raw_data_path = os.path.join(cfg.get('industry_classify', 'raw_data_path'), 'industry_classify_sw.csv')
    classify_data = [['证券代码', '申万行业代码', '申万行业名称']]
    with open(raw_data_path, 'r', newline='') as f:
        f.readline()
        csv_reader = csv.reader(f, delimiter='\t')
        for row in csv_reader:
            code = 'SH' + row[1] if row[1][0] == '6' else 'SZ' + row[1]
            ind_name = row[0]
            ind_code = df_sw_classify[df_sw_classify.ind_name == ind_name].iloc[0].ind_code
            classify_data.append([code, ind_code, ind_name])
    # 保存股票行业分类文件
    classify_data_path = os.path.join(cfg.get('industry_classify', 'classify_data_path'), 'industry_classify_sw.csv')
    with open(classify_data_path, 'w', newline='') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerows(classify_data)


if __name__ == '__main__':
    load_industry_classify()
    # import requests
    # url = 'http://www.swsindex.com/downloadfiles.aspx?swindexcode=SwClass&type=530&columnid=8892'
    # resp = requests.get(url)
    # print(resp.content)

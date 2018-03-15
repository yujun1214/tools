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
from pandas import DataFrame
import requests
import re
import json


def download_sw_fyjr_classify():
    """通过tushare下载申万非银金融下二级行业的分类数据"""
    df_sw_fyjr = DataFrame()
    sw_fyjr = [['sw2_490100', '证券'], ['sw2_490200', '保险'], ['sw2_490300', '多元金融']]
    for industry_info in sw_fyjr:
        url = 'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=1&num=1000&sort=symbol&asc=1&node=%s&symbol=&_s_r_a=page' % industry_info[0]
        text = requests.get(url).text
        reg = re.compile(r'\,(.*?)\:')
        text = reg.sub(r',"\1":', text)
        text = text.replace('"{symbol', '{"symbol')
        text = text.replace('{symbol', '{"symbol"')
        jstr = json.dumps(text)
        js = json.loads(jstr)
        df = pd.DataFrame(pd.read_json(js, dtype={'code': object}), columns=['code','symbol','name','changepercent','trade','open','high','low','settlement','volume','turnoverratio'])
        df['c_name'] = industry_info[1]
        df_sw_fyjr = df_sw_fyjr.append(df[['code', 'name', 'c_name']], ignore_index=True)

    cfg = ConfigParser()
    cfg.read('config.ini')
    file_path = os.path.join(cfg.get('industry_classify', 'raw_data_path'), 'sw_fyjr_classify.csv')
    df_sw_fyjr.to_csv(file_path, index=False)


def load_industry_classify(standard='sw'):
    """导入个股行业分类数据"""
    cfg = ConfigParser()
    cfg.read('config.ini')
    # 读取申万一级行业信息
    sw_classify_info_path = os.path.join(cfg.get('industry_classify', 'classify_data_path'), 'classify_standard_sw.csv')
    df_sw_classify = pd.read_csv(sw_classify_info_path, names=['ind_code', 'ind_name'], header=0)
    # 读取申万非银金融下二级行业信息
    sw_fyjr_classify_path = os.path.join(cfg.get('industry_classify', 'raw_data_path'), 'sw_fyjr_classify.csv')
    df_sw_fyjr_classify = pd.read_csv(sw_fyjr_classify_path, dtype={'code': object}, header=0)
    # 读取股票最新行业分类原始数据，导入本系统的股票申万一级行业分类数据文件
    # 同时把非银金融一级行业替换成二级行业
    raw_data_path = os.path.join(cfg.get('industry_classify', 'raw_data_path'), 'industry_classify_sw.csv')
    classify_data = [['证券代码', '申万行业代码', '申万行业名称']]
    with open(raw_data_path, 'r', newline='') as f:
        f.readline()
        csv_reader = csv.reader(f, delimiter='\t')
        for row in csv_reader:
            code = 'SH' + row[1] if row[1][0] == '6' else 'SZ' + row[1]
            ind_name = row[0]
            if row[1] in df_sw_fyjr_classify['code'].values:
                ind_name = df_sw_fyjr_classify[df_sw_fyjr_classify.code == row[1]].iloc[0].c_name
            ind_code = df_sw_classify[df_sw_classify.ind_name == ind_name].iloc[0].ind_code
            classify_data.append([code, ind_code, ind_name])
    # 保存股票行业分类文件
    classify_data_path = os.path.join(cfg.get('industry_classify', 'classify_data_path'), 'industry_classify_sw.csv')
    with open(classify_data_path, 'w', newline='') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerows(classify_data)


if __name__ == '__main__':
    download_sw_fyjr_classify()
    load_industry_classify()
    # import requests
    # url = 'http://www.swsindex.com/downloadfiles.aspx?swindexcode=SwClass&type=530&columnid=8892'
    # resp = requests.get(url)
    # print(resp.content)

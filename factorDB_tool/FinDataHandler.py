#!/usr/bin/env/ python3
# -*- coding: utf-8 -*-
# @Abstract: 下载上市公司财务数据
# @Filename: FinDataHandler
# @Date:   : 2018-01-12 01:05
# @Author  : YuJun
# @Email   : yujun_mail@163.com


from configparser import ConfigParser
import os
import pandas as pd
from pandas import DataFrame
from jaqs.data.dataapi import DataApi
import requests


def load_fin_data_basics():
    """导入上市公司主要财务指标"""
    cfg = ConfigParser()
    cfg.read('config.ini')
    zycwzb_url = cfg.get('fin_data', 'zycwzb_url')
    db_path = os.path.join(cfg.get('factor_db', 'db_path'), cfg.get('fin_data', 'db_path'))
    # 读取个股代码
    data_api = DataApi(addr='tcp://data.tushare.org:8910')
    data_api.login('13811931480', 'eyJhbGciOiJIUzI1NiJ9.eyJjcmVhdGVfdGltZSI6IjE1MTI4Nzk0NTI2MjkiLCJpc3MiOiJhdXRoMCIsImlkIjoiMTM4MTE5MzE0ODAifQ.I0SXsA1bK--fbGu0B5Is2xdKOjALAeWBJRX6GdVmUL8')
    df_stock_basics, msg = data_api.query(view='jz.instrumentInfo',
                                          fields='status,list_date,name,market',
                                          filter='inst_type=1&status=1&market=SH,SZ&symbol=',
                                          data_format='pandas')
    if msg != '0,':
        print('读取市场个股代码失败。')
        return
    df_stock_basics.symbol = df_stock_basics.symbol.map(lambda x: x.split('.')[0])
    # 遍历个股，下载财务数据
    for _, stock_info in df_stock_basics.iterrows():
        url = zycwzb_url % stock_info.symbol
        resp = requests.get(url)
        if resp.status_code != requests.codes.ok:
            print('%s的财务数据下载失败!' % stock_info.symbol)
            continue
        print('下载%s的主要财务指标数据.' % stock_info.symbol)
        fin_data = resp.text
        fin_data = fin_data.replace('\r\n\t\t', '')
        fin_data = fin_data.split('\r\n')
        fin_datas = []
        for data in fin_data:
            s = data.split(',')
            fin_datas.append(s[:-1])
        dict_fin_data = {data[0]: data[1:] for data in fin_datas}
        fin_header =[data[0] for data in fin_datas]
        df_fin_data = DataFrame(dict_fin_data, columns=fin_header)
        df_fin_data = df_fin_data.sort_values(by=fin_header[0])
        df_fin_data.to_csv(os.path.join(db_path, '%s.csv' % stock_info.symbol),index=False)


if __name__ == '__main__':
    load_fin_data_basics()

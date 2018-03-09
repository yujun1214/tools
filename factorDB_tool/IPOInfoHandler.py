#!/usr/bin/env/ python3
# -*- coding: utf-8 -*-
# @Abstract: 下载股票IPO信息
# @Filename: IpoInfoHandler
# @Date:   : 2018-03-09 15:07
# @Author  : YuJun
# @Email   : yujun_mail@163.com


from configparser import ConfigParser
from pathlib import Path
from jaqs.data.dataapi import DataApi
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pandas import DataFrame
from pandas import Series
import utils
import time


def load_ipo_info():
    """从网易财经下载个股的IPO数据"""
    cfg = ConfigParser()
    cfg.read('config.ini')
    ipo_info_url = cfg.get('ipo_info', 'ipo_info_url')
    db_path = Path(cfg.get('factor_db', 'db_path'), cfg.get('ipo_info', 'db_path'))
    # 读取所有已上市个股代码
    data_api = DataApi(addr='tcp://data.tushare.org:8910')
    data_api.login('13811931480', 'eyJhbGciOiJIUzI1NiJ9.eyJjcmVhdGVfdGltZSI6IjE1MTI4Nzk0NTI2MjkiLCJpc3MiOiJhdXRoMCIsImlkIjoiMTM4MTE5MzE0ODAifQ.I0SXsA1bK--fbGu0B5Is2xdKOjALAeWBJRX6GdVmUL8')
    df_stock_basics, msg = data_api.query(view='jz.instrumentInfo',
                                          fields='status,list_date,name,market',
                                          filter='inst_type=1&status=&market=SH,SZ&symbol=',
                                          data_format='pandas')
    if msg != '0,':
        print('读取市场个股代码失败。')
        return
    df_stock_basics.symbol = df_stock_basics.symbol.map(lambda x: x.split('.')[0])
    # 遍历个股, 下载ipo信息数据
    df_ipo_info = DataFrame()
    for _, stock_info in df_stock_basics.iterrows():
        print('下载%s的IPO数据.' % stock_info.symbol)
        ipo_info_header = []
        ipo_info_data = []

        secu_code = utils.code_to_symbol(stock_info.symbol)
        url = ipo_info_url % stock_info.symbol
        html = requests.get(url).content
        soup = BeautifulSoup(html, 'html.parser')
        tags = soup.find_all(name='h2')
        for tag in tags:
            if tag.get_text().strip() == 'IPO资料':
                ipo_table = tag.find_next(name='table')
                for tr in ipo_table.find_all(name='tr'):
                    tds = tr.find_all(name='td')
                    name = tds[0].get_text().replace(' ', '').replace('\n', '').replace('\r', '')
                    value = tds[1].get_text().replace(' ', '').replace(',','').replace('\n', '').replace('\r', '')
                    ipo_info_header.append(name)
                    ipo_info_data.append(value)
                ipo_info = Series(ipo_info_data, index=ipo_info_header)
                ipo_info['代码'] = secu_code
                ipo_info.to_csv(db_path.joinpath('%s.csv' % secu_code))
                df_ipo_info = df_ipo_info.append(ipo_info, ignore_index=True)
                break
    df_ipo_info.to_csv(db_path.joinpath('ipo_info.csv'), index=False)


if __name__ == '__main__':
    load_ipo_info()

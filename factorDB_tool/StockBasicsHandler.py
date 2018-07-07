#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Abstract: 
# @Filename: StockBasicsHandler
# @Date:   : 2018-07-04 20:52
# @Author  : YuJun
# @Email   : yujun_mail@163.com


from configparser import ConfigParser
import os
import tushare as ts
import utils
import pandas as pd
import requests

def load_stock_basics(date=None):
    """
    导入个股基本信息数据
    --------
    :param date: str
        日期, 默认为上一个交易日
    :return: 保存个股基本信息数据至stock_basics.csv文件
    --------
        0. code 个股代码
        1. name 个股名称
        2. listed_date 上市日期
    """
    stock_basics = ts.get_stock_basics(date)

    stock_basics.loc['000333', 'timeToMarket'] = 20130918
    stock_basics.loc['601360', 'timeToMarket'] = 20180228

    stock_basics.reset_index(inplace=True)
    stock_basics['symbol'] = stock_basics['code'].map(utils.code_to_symbol)
    stock_basics = stock_basics[['symbol', 'name', 'timeToMarket']]
    stock_basics = stock_basics[stock_basics['timeToMarket'] > 0]
    stock_basics.rename(columns={'timeToMarket': 'listed_date'}, inplace=True)

    # stock_basics = stock_basics.append(pd.Series(['SH601313', '江南嘉捷', 20120116], index=['symbol', 'name', 'listed_date']), ignore_index=True)

    stock_basics.sort_values(by='symbol', inplace=True)

    cfg = ConfigParser()
    cfg.read('config.ini')
    factor_db_path = cfg.get('factor_db', 'db_path')
    stock_basics_path = os.path.join(factor_db_path, cfg.get('stock_basics', 'db_path'), 'stock_basics.csv')
    stock_basics.to_csv(stock_basics_path, index=False)

def load_st_info():
    """导入个股st带帽摘帽时间信息"""
    cfg = ConfigParser()
    cfg.read('config.ini')
    factor_db_path = cfg.get('factor_db', 'db_path')
    raw_data_path = cfg.get('st_info', 'raw_data_path')
    st_info_path = cfg.get('st_info', 'st_info_path')
    st_start_types = cfg.get('st_info', 'st_start_types').split(',')
    st_end_types = cfg.get('st_info', 'st_end_types').split(',')

    df_st_rawinfo = pd.read_csv(os.path.join(raw_data_path, 'st_info.csv'), header=0)
    df_st_rawinfo = df_st_rawinfo[df_st_rawinfo['st_info'] != '0']
    df_st_info = pd.DataFrame(columns=['code', 'st_start', 'st_end'])
    for _, st_data in df_st_rawinfo.iterrows():
        st_start_date = None
        st_end_date = None

        code = utils.code_to_symbol(st_data['code'])
        st_info_list = st_data['st_info'].split(',')
        st_info_list = st_info_list[::-1]
        for st_info in st_info_list:
            if '：' in st_info:
                st_type = st_info.split('：')[0]
                st_date = st_info.split('：')[1]
                if not (st_type in st_start_types or st_type in st_end_types):
                    print('st type: {} is not counted.'.format(st_type))
                    continue
                if st_type in st_start_types and st_start_date is None:
                    st_start_date = st_date
                elif st_type in st_end_types and st_start_date is not None:
                    st_end_date = st_date
                    df_st_info = df_st_info.append(pd.Series([code, st_start_date, st_end_date], index=['code', 'st_start', 'st_end']), ignore_index=True)
                    st_start_date = None
                    st_end_date = None
        if st_start_date is not None and st_end_date is None:
            df_st_info = df_st_info.append(pd.Series([code, st_start_date, '20301231'], index=['code', 'st_start', 'st_end']), ignore_index=True)
    df_st_info.to_csv(os.path.join(factor_db_path, st_info_path, 'st_info.csv'), index=False)

def load_calendar():
    """导入交易日历数据"""
    cfg = ConfigParser()
    cfg.read('config.ini')
    calendar_url = cfg.get('calendar', 'calendar_url')
    calendar_path = os.path.join(cfg.get('factor_db', 'db_path'), cfg.get('calendar', 'calendar_path'), 'trading_days.csv')

    calendar_resp = requests.get(calendar_url)
    calendar_data = pd.Series(calendar_resp.text.split('\n')[1:-1], name='trading_day')
    calendar_data.to_csv(calendar_path, index=False, header=True)



if __name__ == '__main__':
    load_stock_basics()
    # load_st_info()
    # load_calendar()

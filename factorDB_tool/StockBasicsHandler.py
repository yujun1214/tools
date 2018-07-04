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
    stock_basics.reset_index(inplace=True)
    stock_basics['symbol'] = stock_basics['code'].map(utils.code_to_symbol)
    stock_basics = stock_basics[['symbol', 'name', 'timeToMarket']]
    stock_basics = stock_basics[stock_basics['timeToMarket'] > 0]
    stock_basics.rename(columns={'timeToMarket': 'listed_date'}, inplace=True)
    stock_basics.sort_values(by='symbol', inplace=True)

    cfg = ConfigParser()
    cfg.read('config.ini')
    factor_db_path = cfg.get('factor_db', 'db_path')
    stock_basics_path = os.path.join(factor_db_path, cfg.get('stock_basics', 'db_path'), 'stock_basics.csv')
    stock_basics.to_csv(stock_basics_path, index=False)



if __name__ == '__main__':
    load_stock_basics()

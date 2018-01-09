#!/usr/bin/env/ python3
# -*- coding: utf-8 -*-
# @Abstract: 集中处理多因子数据库的数据导入
# @Filename: DataHandler
# @Date:   : 2018-01-09 19:32
# @Author  : YuJun
# @Email   : yujun_mail@163.com

import MktDataHandler as mkt
import CapStructHandler as cap_struct
import IndustryClassifyHandler as ind_cls

if __name__ == '__main__':
    str_date = '2018-01-09'
    print(str_date)
    # 导入复权分钟数据
    print('导入复权分钟行情数据...')
    mkt.load_mkt_1min(str_date.replace('-', ''), 'D')
    # 导入日线行情数据
    print('导入日线行情数据...')
    mkt.load_mkt_daily(True, str_date)
    # 导入股票股本结构数据
    print('导入股票股本结构数据...')
    cap_struct.load_cap_struct()
    # 导入最新行业分类数据
    print('导入申万行业分类数据...')
    ind_cls.load_industry_classify('sw')

#!/usr/bin/env/ python3
# -*- coding: utf-8 -*-
# @Abstract: 导入股本结构数据
# @Filename: CapStructHandler
# @Date:   : 2018-01-05 23:45
# @Author  : YuJun
# @Email   : yujun_mail@163.com

from configparser import ConfigParser
import os
import pandas as pd


def load_cap_struct():
    """导入个股最新股本结构数据"""
    cfg = ConfigParser()
    cfg.read('config.ini')
    raw_data_path = cfg.get('cap_struct', 'raw_data_path')
    db_path = cfg.get('cap_struct', 'db_path')
    df_cap_struct = pd.read_csv(os.path.join(raw_data_path, 'cap_struct.csv'),
                                names=['mkt', 'code', 'date', 'reason', 'total', 'liquid_a', 'liquid_b', 'liquid_h'],
                                header=0, encoding='GB18030', dtype={'code': str})
    df_cap_struct.code = df_cap_struct.apply(lambda x: x.mkt + x.code, axis=1)
    del df_cap_struct['mkt']
    # 先保存全部股本结构数据为一个文件
    df_cap_struct.to_csv(os.path.join(db_path, 'cap_struct.csv'), index=False,
                         header=['代码', '变更日期', '变更原因', '总股本', '流通A股', '流通B股', '流通H股'])
    # 然后每个个股分别保存一个股本结构数据文件
    codes = df_cap_struct.code.unique()
    for code in codes:
        print('processing capital structure data of %s.' % code)
        df_single_cap_struct = df_cap_struct[df_cap_struct.code == code]
        df_single_cap_struct.to_csv(os.path.join(db_path, code+'.csv'), index=False,
                                    header=['代码', '变更日期', '变更原因', '总股本', '流通A股', '流通B股', '流通H股'])


if __name__ == '__main__':
    load_cap_struct()

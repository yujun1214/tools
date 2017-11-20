#!/usr/bin/env/ python3
# -*- coding: utf-8 -*-
# @Filename: MktDataHandler
# @Date:   : 2017-10-18 18:01
# @Author  : YuJun
# @Email   : yujun_mail@163.com

from configparser import ConfigParser
import os
import csv


def load_mkt_1min(tm, tmtype):
    """
    导入股票分钟行情数据
    :param tm: 当tmtype=Y时，为年份（如，2017）；当tmtype=D时，为日期数据（如，20171017）
    :param tmtype: 日期类型，Y：代表导入tm参数指定的年度数据；D：代表导入tm指定的天数据
    :return:
    """
    cfg = ConfigParser()
    cfg.read('config.ini')
    raw_data_path = os.path.join(cfg.get('mkt_data_handler', 'raw_data_path'), 'Stk_Min1_FQ_%s' % tm)
    db_path = os.path.join(cfg.get('factor_db', 'db_path'), 'ElementaryFactor', 'mkt_1min_FQ')

    if tmtype == 'Y':
        for mkt_file_name in os.listdir(raw_data_path):
            dst_file_name = mkt_file_name.upper()
            mkt_file_path = os.path.join(raw_data_path, mkt_file_name)
            print('processing file %s' % mkt_file_path)
            if os.path.isfile(mkt_file_path):
                pre_strDate = ''
                with open(mkt_file_path, newline='', encoding='GB18030') as rawFile:
                    strHeader = rawFile.readline()
                    csvReader = csv.reader(rawFile)
                    dstRows = []
                    for row in csvReader:
                        strDate = row[1][:10]
                        if len(pre_strDate) == 0:
                            pre_strDate = strDate
                        if strDate != pre_strDate and len(pre_strDate) > 0:
                            if os.path.exists(os.path.join(db_path, pre_strDate)) == False:
                                os.mkdir(os.path.join(db_path, pre_strDate))
                            with open(os.path.join(db_path, pre_strDate, dst_file_name), 'w', newline='') as dstFile:
                                dstFile.write(strHeader)
                                csvWriter = csv.writer(dstFile)
                                csvWriter.writerows(dstRows)
                            dstRows = []
                            pre_strDate = strDate
                        dstRows.append(row)
                    if len(dstRows) > 0:
                        if os.path.exists(os.path.join(db_path, pre_strDate)) == False:
                            os.mkdir(os.path.join(db_path, pre_strDate))
                        with open(os.path.join(db_path, pre_strDate, dst_file_name), 'w', newline='') as dstFile:
                            dstFile.write(strHeader)
                            csvWriter = csv.writer(dstFile)
                            csvWriter.writerows(dstRows)


if __name__ == '__main__':
    load_mkt_1min('2016', 'Y')

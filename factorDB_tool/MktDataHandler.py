#!/usr/bin/env/ python3
# -*- coding: utf-8 -*-
# @Filename: MktDataHandler
# @Date:   : 2017-10-18 18:01
# @Author  : YuJun
# @Email   : yujun_mail@163.com

from configparser import ConfigParser
import os
import csv
import datetime
import pandas as pd


def load_mkt_1min(tm, tmtype):
    """
    导入股票分钟行情数据
    :param tm: 当tmtype=Y时，为年份（如，'2017'）；当tmtype=D时，为日期数据（如，'20171017'）
    :param tmtype: 日期类型，Y：代表导入tm参数指定的年度数据；D：代表导入tm指定的天数据
    :return:
    """
    cfg = ConfigParser()
    cfg.read('config.ini')
    if tmtype == 'Y':
        raw_data_path = os.path.join(cfg.get('mkt_data_1min', 'raw_data_path'), 'Stk_Min1_FQ_%s' % tm)
    elif tmtype == 'D':
        raw_data_path = os.path.join(cfg.get('mkt_data_1min', 'raw_data_path'), tm)
    else:
        print('Wrong tmtype.')
        return
    db_path = os.path.join(cfg.get('factor_db', 'db_path'), cfg.get('mkt_data_1min', 'db_path'))

    for mkt_file_name in os.listdir(raw_data_path):
        if os.path.splitext(mkt_file_name)[1] != '.csv':
            continue
        mkt_file_path = os.path.join(raw_data_path, mkt_file_name)
        # print('processing file %s' % mkt_file_path)
        _write_1min_FQ_data(mkt_file_path, db_path)

    # if tmtype == 'Y':
    #     for mkt_file_name in os.listdir(raw_data_path):
    #         dst_file_name = mkt_file_name.upper()
    #         mkt_file_path = os.path.join(raw_data_path, mkt_file_name)
    #         print('processing file %s' % mkt_file_path)
    #         if os.path.isfile(mkt_file_path):
    #             _write_1min_FQ_data(mkt_file_path, db_path)
    #             pre_strDate = ''
    #             with open(mkt_file_path, newline='', encoding='GB18030') as rawFile:
    #                 strHeader = rawFile.readline()
    #                 csvReader = csv.reader(rawFile)
    #                 dstRows = []
    #                 for row in csvReader:
    #                     strDate = row[1][:10]
    #                     if len(pre_strDate) == 0:
    #                         pre_strDate = strDate
    #                     if strDate != pre_strDate and len(pre_strDate) > 0:
    #                         if os.path.exists(os.path.join(db_path, pre_strDate)) == False:
    #                             os.mkdir(os.path.join(db_path, pre_strDate))
    #                         with open(os.path.join(db_path, pre_strDate, dst_file_name), 'w', newline='') as dstFile:
    #                             dstFile.write(strHeader)
    #                             csvWriter = csv.writer(dstFile)
    #                             csvWriter.writerows(dstRows)
    #                         dstRows = []
    #                         pre_strDate = strDate
    #                     dstRows.append(row)
    #                 if len(dstRows) > 0:
    #                     if os.path.exists(os.path.join(db_path, pre_strDate)) == False:
    #                         os.mkdir(os.path.join(db_path, pre_strDate))
    #                     with open(os.path.join(db_path, pre_strDate, dst_file_name), 'w', newline='') as dstFile:
    #                         dstFile.write(strHeader)
    #                         csvWriter = csv.writer(dstFile)
    #                         csvWriter.writerows(dstRows)

def _write_1min_FQ_data(mkt_file_path, db_path):
    """
    写入个股分钟复权行情数据至数据库
    :param mkt_file_path: 原始的分钟复权行情数据文件路径
    :param db_path: 复权分钟行情在数据库中的路径
    :return:
    """
    mkt_file_name = os.path.basename(mkt_file_path)     # 原始行情文件名
    dst_file_name = mkt_file_name.upper()               # 目标行情文件名
    if os.path.isfile(mkt_file_path):
        pre_strDate = ''
        with open(mkt_file_path, newline='', encoding='GB18030') as raw_file:
            str_header = raw_file.readline()
            csv_reader = csv.reader(raw_file)
            dst_rows = []
            for row in csv_reader:
                str_date = row[1][:10]
                if len(pre_strDate) == 0:
                    pre_strDate = str_date
                if str_date != pre_strDate and len(pre_strDate) > 0:
                    if os.path.exists(os.path.join(db_path, pre_strDate)) == False:
                        os.mkdir(os.path.join(db_path, pre_strDate))
                    if pre_strDate > '2016-10-31':
                        with open(os.path.join(db_path, pre_strDate, dst_file_name), 'w', newline='') as dst_file:
                            dst_file.write(str_header)
                            csv_writer = csv.writer(dst_file)
                            csv_writer.writerows(dst_rows)
                    dst_rows = []
                    pre_strDate = str_date
                dst_rows.append(row)
            if len(dst_rows) > 0:
                if os.path.exists(os.path.join(db_path, pre_strDate)) == False:
                    os.mkdir(os.path.join(db_path, pre_strDate))
                with open(os.path.join(db_path, pre_strDate, dst_file_name), 'w', newline='') as dst_file:
                    dst_file.write(str_header)
                    csv_writer = csv.writer(dst_file)
                    csv_writer.writerows(dst_rows)


def load_mkt_daily(is_one_day=False, str_date=None, is_index_data=False):
    """
    导入个股复权日行情数据至因子数据库，同时导入到复权行情因子库和不复权行情因子库
    :param is_one_day: bool, 是否导入一天的数据，默认False
    :param str_date: str, 格式：YYYY-MM-DD
        当is_one_day=True时，指定导入的日期。如果is_one_day=True,str_date=None，则导入当天的行情数据
    :param is_index_data, bool，默认False
        是否是指数历史数据
    :return:
    """
    cfg = ConfigParser()
    cfg.read('config.ini')
    raw_data_path = cfg.get('mkt_data_daily', 'raw_data_path')
    raw_data_path_by_daily = cfg.get('mkt_data_daily', 'raw_data_path_by_daily')
    raw_data_path_idx = cfg.get('mkt_data_daily', 'raw_data_path_idx')
    if is_one_day and is_index_data:
        print("导入一天的日线数据，'is_index_data'参数值不能为True.")
        return
    if is_one_day:
        if str_date is None:
            str_date = datetime.date.today().strftime('%Y%m%d')
            raw_data_path_by_daily += '/%s.csv' % str_date
        else:
            str_date = str_date.replace('-', '')
            raw_data_path_by_daily += '/%s.csv' % str_date
    db_path_fq = os.path.join(cfg.get('factor_db', 'db_path'), cfg.get('mkt_data_daily', 'db_path_FQ'))
    db_path_nofq = os.path.join(cfg.get('factor_db', 'db_path'), cfg.get('mkt_data_daily', 'db_path_NoFQ'))

    if is_one_day:
        if os.path.isfile(raw_data_path_by_daily):
            # print('processing file %s' % raw_data_path_by_daily)
            with open(raw_data_path_by_daily, 'r', newline='', encoding='GB18030') as raw_file:
                csv_reader = csv.reader(raw_file)
                str_header_FQ = next(csv_reader)
                str_header_NoFQ = str_header_FQ[1:-1]
                for row in csv_reader:
                    code = row[0].upper()
                    # print('[%s] processing intrument %s' % (str_date, code))
                    # 保存复权日线数据
                    mkt_file_path = os.path.join(db_path_fq, '%s.csv' % code)
                    if os.path.exists(mkt_file_path):
                        # df_mkt_data = pd.read_csv(mkt_file_path, names=['code', 'date', 'open', 'high', 'low',
                        #                                                 'close', 'vol', 'amount', 'to1', 'to2',
                        #                                                 'factor'], header=0)
                        df_mkt_data = pd.read_csv(mkt_file_path, names=['code', 'date'], usecols=range(2), header=0)
                        if datetime.datetime.strptime(str_date, '%Y%m%d').strftime('%Y-%m-%d') not in list(df_mkt_data['date']):
                            with open(mkt_file_path, 'a') as dst_fq_file:
                                dst_fq_file.write(','.join(row) + '\n')
                    else:
                        with open(mkt_file_path, 'w') as dst_fq_file:
                            dst_fq_file.write(','.join(str_header_FQ) + '\n')
                            dst_fq_file.write(','.join(row) + '\n')
                    # 保存非复权日线数据
                    mkt_file_path = os.path.join(db_path_nofq, '%s.csv' % code)
                    mkt_date = row[1]
                    factor = float(row[10])
                    fopen = float(row[2])/factor
                    fhigh = float(row[3])/factor
                    flow = float(row[4])/factor
                    fclose = float(row[5])/factor
                    mkt_data_row = [mkt_date, str(round(fopen,2)), str(round(fhigh,2)), str(round(flow,2)),
                                    str(round(fclose,2)), row[6], row[7], row[8], row[9]]
                    if os.path.exists(mkt_file_path):
                        # df_mkt_data = pd.read_csv(mkt_file_path, names=['date', 'open', 'high', 'low', 'close', 'vol',
                        #                                                 'amount', 'to1', 'to2'], header=0)
                        df_mkt_data = pd.read_csv(mkt_file_path, names=['date'], usecols=range(1), header=0)
                        if datetime.datetime.strptime(str_date, '%Y%m%d').strftime('%Y-%m-%d') not in list(df_mkt_data['date']):
                            with open(mkt_file_path, 'a') as dst_nofq_file:
                                dst_nofq_file.write(','.join(mkt_data_row) + '\n')
                    else:
                        with open(mkt_file_path, 'w') as dst_nofq_file:
                            dst_nofq_file.write(','.join(str_header_NoFQ) + '\n')
                            dst_nofq_file.write(','.join(mkt_data_row) + '\n')
    elif is_index_data:
        for mkt_file_name in os.listdir(raw_data_path_idx):
            if os.path.splitext(mkt_file_name)[1] != '.csv':
                continue
            dst_file_name = mkt_file_name.upper()
            mkt_file_path = os.path.join(raw_data_path_idx, mkt_file_name)
            print('processing file %s' % mkt_file_path)
            if os.path.isfile(mkt_file_path):
                with open(mkt_file_path, 'r', newline='', encoding='GB18030') as raw_file:
                    dst_rows_fq = []
                    dst_rows_nofq = []
                    csv_reader = csv.reader(raw_file)
                    raw_header = next(csv_reader)
                    for row in csv_reader:
                        fq_row = row + ['0', '0', '1']
                        # fq_row.extend(['0', '0', '1'])
                        dst_rows_fq.append(fq_row)
                        nofq_row = row[1:] + ['0', '0']
                        # nofq_row.extend(['0', '0'])
                        dst_rows_nofq.append(nofq_row)
                with open(os.path.join(db_path_fq, dst_file_name), 'w', newline='') as dst_fq_file:
                    csv_writer = csv.writer(dst_fq_file)
                    fq_header = raw_header + ['流通盘换手率', '全流通换手率', '复权系数']
                    csv_writer.writerow(fq_header)
                    csv_writer.writerows(dst_rows_fq)
                with open(os.path.join(db_path_nofq, dst_file_name), 'w', newline='') as dst_nofq_file:
                    csv_writer = csv.writer(dst_nofq_file)
                    nofq_header = raw_header[1:] + ['流通盘换手率', '全流通换手率']
                    csv_writer.writerow(nofq_header)
                    csv_writer.writerows(dst_rows_nofq)
    else:
        for mkt_file_name in os.listdir(raw_data_path):
            # 过滤隐藏文件
            # if mkt_file_name[0] == '.':
            #     continue
            if os.path.splitext(mkt_file_name)[1] != '.csv':
                continue
            dst_file_name = mkt_file_name.upper()
            mkt_file_path = os.path.join(raw_data_path, mkt_file_name)
            print('processing file %s' % mkt_file_path)
            if os.path.isfile(mkt_file_path):
                with open(mkt_file_path, 'r', newline='', encoding='GB18030') as rawFile:
                    # 导入复权行情至复权行情因子库
                    if not os.path.exists(db_path_fq):
                        os.mkdir(db_path_fq)
                    with open(os.path.join(db_path_fq, dst_file_name), 'w', newline='') as dstFQFile:
                        dstFQFile.write(rawFile.read())
                    # 将复权行情转换为非复权行情，并导入至非复权行情因子库
                    rawFile.seek(0, 0)
                    csvReader = csv.reader(rawFile)
                    head_row = next(csvReader)
                    dstRows = []
                    if len(head_row) < 10:
                        head_row = head_row[1:]
                        for row in csvReader:
                            dstRows.append(row[1:])
                    else:
                        head_row = head_row[1:-1]
                        for row in csvReader:
                            mkt_date = row[1]
                            factor = float(row[10])
                            fopen = float(row[2])/factor
                            fhigh = float(row[3])/factor
                            flow = float(row[4])/factor
                            fclose = float(row[5])/factor
                            dstRows.append([mkt_date, str(round(fopen,2)), str(round(fhigh,2)), str(round(flow,2)),
                                            str(round(fclose,2)), row[6], row[7], row[8], row[9]])
                    with open(os.path.join(db_path_nofq, dst_file_name), 'w', newline='') as dstNoFQFile:
                        csvWriter = csv.writer(dstNoFQFile)
                        csvWriter.writerow(head_row)
                        csvWriter.writerows(dstRows)


if __name__ == '__main__':
    load_mkt_1min('20180109', 'D')

    load_mkt_daily(is_one_day=True, str_date='2018-01-09', is_index_data=False)

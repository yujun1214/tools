#!/usr/bin/env/ python3
# -*- coding: utf-8 -*-
# @Abstract: 从一致预期原始数据文件中导入一致预期数据至一致数据库
# @Filename: ConsensusDataHandler
# @Date:   : 2018-05-15 17:55
# @Author  : YuJun
# @Email   : yujun_mail@163.com


from configparser import ConfigParser
import os
import pandas as pd


def load_predictedearning_data(date=None):
    """
    导入股票盈利预期(未来12个月)原始数据至因子数据库
    Parameters:
    --------
    :param date: str, 默认为None
        导入盈利预期数据对应的交易日期, 格式: YYYY-MM-DD
        若为None则导入总体数据(从PredictedEarnings.csv文件导入);
        若指定交易日期，则导入对应日期的盈利预期数据(从PredictedEarnings_YYYYMMDD.csv文件导入)
    :return:
    """
    cfg = ConfigParser()
    cfg.read('config.ini')
    factor_db_path = cfg.get('factor_db', 'db_path')
    predictedearnings_data_path = cfg.get('consensus_data', 'predictedearnings_path')
    if date is None:
        # 如果日期为None, 从PredictedEarnings.csv文件导入盈利预期数据
        raw_data_path = os.path.join(cfg.get('consensus_data', 'consensus_raw_path'), 'PredictedEarnings.csv')
        df_predictedearnings = pd.read_csv(raw_data_path, header=0, index_col=0)
        for strdate in df_predictedearnings.columns.values.tolist():
            print('Loading Predicted Earnings data of {}.'.format(strdate))
            predictedearnings_data = df_predictedearnings[strdate]
            predictedearnings_data = predictedearnings_data[predictedearnings_data.abs() > 0]
            predictedearnings_data.rename(index='predicted_earnings', inplace=True)
            dst_data_path = os.path.join(factor_db_path, predictedearnings_data_path, 'predictedearnings_{}.csv'.format(strdate))
            predictedearnings_data.to_csv(dst_data_path, index=True, header=True)
    else:
        # 如果指定交易日期, 从PredictedEarnings_YYYYMMDD.csv文件导入盈利预期数据
        str_date = date.replace('-', '')
        print('Loaidng Predicted Earning data of {}.'.format(str_date))
        raw_data_path = os.path.join(cfg.get('consensus_data', 'consensus_raw_path'), 'PredictedEarnings_{}.csv'.format(str_date))
        df_predictedearnings = pd.read_csv(raw_data_path, header=0, index_col=0)
        df_predictedearnings = df_predictedearnings[df_predictedearnings.abs() > 0]
        df_predictedearnings.rename(index='predicted_earnings', inplace=True)
        dst_data_path = os.path.join(factor_db_path, predictedearnings_data_path, 'predictedearnings_{}.csv'.format(str_date))
        df_predictedearnings.to_csv(dst_data_path, index=True, header=True)


if __name__ == '__main__':
    # pass
    load_predictedearning_data()

from configparser import ConfigParser
import requests
import re
import time
import datetime
import math
from scipy.stats import norm
import tushare as ts
import numpy as np

# 全局变量
PRE_UNDERLYING_PRICE = 0.0      # 前一次计算Greeks所用的标的价格
UNDERLYING_PRICE = 0.0          # 当前最新的标的价格
RISK_FREE = 0.0                 # 无风险利率，一年期shibor拆放利率
DIVIDEND_RATE = 0.0             # 股息率
UNDERLYING_VOL = 0.0            # 标的的波动率


class OptRtMktData(object):
    """50ETF期权（含50ETF）实时行情下载类"""

    def __init__(self):
        """导入配置信息，进行初始化"""
        cfg = ConfigParser()
        cfg.read('config.ini')
        self.interval = cfg.getint('mktdata', 'interval')
        self.server = cfg.get('mktdata', 'server')
        self.paths = cfg.get('mktdata', 'paths').split(',')
        self.months = cfg.get('mktdata', 'months').split(',')
        self.underlyingcode = 'sh510050'
        self.optcodes = self.get_opt_codes()

    def download_underlying_rtmktdata(self):
        """下载标的实时行情数据"""
        url = 'http://hq.sinajs.cn/list=sh510050'
        resp = requests.get(url)
        mkts = resp.text.split(sep='="')[1].split(sep=',')[:-1]
        # print(mkts)
        # print(len(mkts))
        self.save_underlying_rtmktdata(mkts)
        # 更新标的最新价格的全局变量
        global UNDERLYING_PRICE
        underlying_last = float(mkts[3])
        UNDERLYING_PRICE = underlying_last
        calc_sseopt_greeks(underlying_last, RISK_FREE, DIVIDEND_RATE, UNDERLYING_VOL)

    def save_underlying_rtmktdata(self, mkts):
        """保存标的实时行情至文件"""
        for path in self.paths:
            with open(path + 'underlying_rt_mkt.csv', 'wt') as f:
                f.write("code,name,open,pre_close,last,high,low,bid,ask,volume,amount,bid_volume1,bid_price1,"
                        "bid_volume2,bid_price2,bid_volume3,bid_price3,bid_volume4,bid_price4,bid_volume5,"
                        "bid_price5,ask_volume1,ask_price1,ask_volume2,ask_price2,ask_volume3,ask_price3,"
                        "ask_volume4,ask_price4,ask_volume5,ask_price5,date,time\n")
                strmktdata = '510050,' + ','.join(mkts)
                f.write(strmktdata)

    def get_opt_codes(self):
        """获取期权代码"""
        callcodes = ['OP_UP_510050%s' % month[-4:] for month in self.months]
        putcodes = ['OP_DOWN_510050%s' % month[-4:] for month in self.months]
        optcodes = callcodes + putcodes
        url = 'http://hq.sinajs.cn/list=%s' % ','.join(optcodes)
        resp = requests.get(url)
        str_pat = re.compile(r'=\"(.*?),\"')
        str_optcodes = ','.join(str_pat.findall(resp.text))
        return str_optcodes.split(',')

    def download_opt_rtmktdata(self):
        """下载期权的实时行情数据"""
        url = 'http://hq.sinajs.cn/list=%s' % ','.join(self.optcodes)
        resp = requests.get(url)
        # print(resp.text)
        # 解析返回行情数据中的期权代码
        str_code_pat = re.compile(r'OP_(.*?)="')
        optcodes = str_code_pat.findall(resp.text)
        # 解析行情数据
        str_mkt_pat = re.compile(r'=\"(.*?)\";')
        mkt_datas = str_mkt_pat.findall(resp.text)
        if len(optcodes) == len(mkt_datas):
            self.save_opt_rtmktdata([code + ',' + mkt_data for code, mkt_data in zip(optcodes, mkt_datas)])

    def save_opt_rtmktdata(self, mkts):
        """保存期权实时行情数据至文件
        Parameter:
        -------
        mkts : 期权行情数据列表，列表的每个元素为一只期权的实时行情数据
        
        期权实时行情数据项分别为：
        0: 期权代码, optcode
        1: 买量, bid_volume(=bid_volume1)
        2: 买价, bid_price(=bid_price1)
        3: 最新价, last
        4: 卖价, ask_price(=ask_price1)
        5: 卖量, ask_volume(=ask_volume1)
        6: 持仓量, open_int
        7: 涨幅, increase
        8: 行权价, strike
        9: 昨收价, pre_close
        10: 开盘价, open
        11: 涨停价, up_limit
        12: 跌停价, down_limit
        13: 申卖价五, ask_price5
        14: 申卖量五, ask_volume5
        15: 申卖价四, ask_price4
        16: 申卖量四, ask_volume4
        17: 申卖价三, ask_price3
        18: 申卖量三, ask_volume3
        19: 申卖价二, ask_price2
        20: 申卖量二, ask_volume2
        21: 申卖价一, ask_price1
        22: 申卖量一, ask_volume1
        23: 申买价一, bid_price1
        24: 申卖量一, bid_volume1
        25: 申买价二, bid_price2
        26: 申买量二, bid_volume2
        27: 申买价三, bid_price3
        28: 申买量三, bid_volume3
        29: 申买价四, bid_price4
        30: 申买量四, bid_volume4
        31: 申买价五, bid_price5
        32: 申买量五, bid_volume5
        33: 行情时间, datetime
        34: 主力合约标识, iszl
        35: 状态码, status
        36: 标的证券类型, underlyingtype
        37: 标的代码, underlyingcode
        38: 期权合约简称, optname
        39: 振幅, swing
        40: 最高价, high
        41: 最低价, low
        42: 成交量, volume
        43: 成交额, amount
        44: 行权价调整标识, adjflag
        """
        if mkts:
            for path in self.paths:
                with open(path + 'option_rt_mkt.csv', 'wt') as f:
                    f.write("optcode,bid_volume,bid_price,last,ask_price,ask_volume,open_int,increase,strike,pre_close,"
                            "open,up_limit,down_limit,ask_price5,ask_volume5,ask_price4,ask_volume4,ask_price3,"
                            "ask_volume3,ask_price2,ask_volume2,ask_price1,ask_volume1,bid_price1,bid_volume1,"
                            "bid_price2,bid_volume2,bid_price3,bid_volume3,bid_price4,bid_volume4,bid_price5,"
                            "bid_volume5,datetime,iszl,status,underlyingtype,underlyingcode,optname,swing,high,"
                            "low,volume,amount,adjflag\n")
                    for mkt in mkts:
                        f.write(mkt + "\n")


class COption(object):
    """期权类"""

    def __init__(self, opt_type, exercise_type, strike, multiplier, end_date):
        """
        初始化期权类
        Parameters:
        --------
        opt_type:期权类型，Call, Put
        exercise_type:行权方式，European, American
        strike:行权价
        multiplier:合约单位
        end_date:到期日，datetime.date类
        """
        self.opt_type = opt_type
        self.exercise_type = exercise_type
        self.strike = strike
        self.multiplier = multiplier
        self.end_date = end_date
        self.delta = 0.0
        self.gamma = 0.0
        self.vega = 0.0
        self.theta = 0.0
        self.rho = 0.0

    def calc_greeks(self, underlying_price, risk_free, dividend_rate, vol):
        """
        计算期权的希腊字母值
        Parameters:
        underlyingprice:标的最新价格
        risk_free:无风险利率，取最新的一年期shibor利率
        dividend_rate:股息率，=0
        vol:波动率，标的的60日历史波动率
        """
        tau = ((self.end_date - datetime.date.today()).days + COption.time_remain_of_day()) / 365.0
        d1 = (math.log(underlying_price / self.strike) +
              (risk_free - dividend_rate + vol * vol / 2.0) * tau) / vol / math.sqrt(tau)
        if self.opt_type.lower() == 'call':
            self.delta = math.exp(-dividend_rate * tau) * norm.cdf(d1)
        elif self.opt_type.lower() == 'put':
            self.delta = math.exp(-dividend_rate * tau) * (norm.cdf(d1) - 1.0)
        else:
            self.delta = 0.0

        self.gamma = (math.exp(-dividend_rate * tau - d1 * d1 / 2.0) / vol / underlying_price /
                      math.sqrt(2.0 * math.pi * tau))
        self.vega = (math.exp(-dividend_rate * tau - d1 * d1 / 2.0) * underlying_price *
                     math.sqrt(tau / 2.0 / math.pi) / 100.0)

    @classmethod
    def time_remain_of_day(cls):
        """计算当天剩余时间（单位=天），主要用于计算期权希腊字母时剩余时间"""
        y = datetime.date.today().year
        m = datetime.date.today().month
        d = datetime.date.today().day
        time_now = datetime.datetime.now()
        if time_now < datetime.datetime(y, m, d, 9, 30, 0, 0):
            time_remain = 1.0
        elif time_now < datetime.datetime(y, m, d, 11, 30, 0, 0):
            time_remain = 1.0 - (time_now - datetime.datetime(y, m, d, 9, 30, 0, 0)).seconds / 14400.0
        elif time_now < datetime.datetime(y, m, d, 13, 0, 0, 0):
            time_remain = 0.5
        elif time_now < datetime.datetime(y, m, d, 15, 0, 0, 0):
            time_remain = (datetime.datetime(y, m, d, 15, 0, 0, 0) - time_now).seconds / 14400.0
        else:
            time_remain = 0.0
        return time_remain


def load_sseopt_data():
    """
    读取上交所股票期权文件数据
    返回期权信息字典,dict<OptCode,COption>
    """
    cfg = ConfigParser()
    cfg.read('config.ini')
    sseopt_file_path = cfg.get('greeks', 'sseoptfilepath')
    sseopt_file_path += 'SSEOptContract' + datetime.date.today().strftime('%Y%m%d') + '.txt'
    dict_opts = {}
    with open(sseopt_file_path, 'rt') as f:
        for line in f:
            single_opt = {}
            opt_items = line.rstrip().split('|')
            for opt_item in opt_items:
                eq_pos = opt_item.find('=')
                if eq_pos > 0:
                    single_opt[opt_item[:eq_pos]] = opt_item[eq_pos + 1:]
            if single_opt['CALL_OR_PUT'] == '认购':
                opt_type = 'Call'
            else:
                opt_type = 'Put'
            exercise_type = 'European'
            strike = float(single_opt['EXERCISE_PRICE'])
            multiplier = int(single_opt['CONTRACT_UNIT'])
            str_end_date = single_opt['END_DATE']
            end_date = datetime.date(int(str_end_date[0:4]), int(str_end_date[4:6]), int(str_end_date[6:]))
            opt_code = single_opt['SECURITY_ID'] + '.SH'
            sse_opt = COption(opt_type, exercise_type, strike,  multiplier, end_date)
            dict_opts[opt_code] = sse_opt
    return dict_opts


def calc_sseopt_greeks(underlying_price, risk_free, dividend_rate, vol):
    """
    计算上交所股票期权希腊字母值的入口函数
    :param underlying_price: 标的最新价格，50ETF
    :param risk_free: 无风险利率，一年期shibor拆放利率
    :param dividend_rate: 股息率=0
    :param vol: 波动率
    :return: 无
    """
    global PRE_UNDERLYING_PRICE
    if underlying_price == PRE_UNDERLYING_PRICE:
        # 如果标的最新价格和前一次计算Greeks时所用的标的价格相同，则不重新计算Greeks
        pass
    else:
        # 读取上交所股票期权文件数据
        dict_sseopts = load_sseopt_data()
        # 遍历每个期权实例对象，计算Greeks
        for optcode, copt in dict_sseopts.items():
            copt.calc_greeks(underlying_price, risk_free, dividend_rate, vol)
        # 保存期权greeks
        save_sseopt_greeks(dict_sseopts, underlying_price)
    # 更新PRE_UNDERLYING_PRICE
    PRE_UNDERLYING_PRICE = underlying_price


def save_sseopt_greeks(dict_sseopts, underlying_price):
    """
    保存上交所股票期权的Greeks
    :param dict_sseopts: 上交所股票期权类字典map<OptCode, COption>
    :param underlying_price: 前一次计算greeks时所用的标的价格
    :return: 无
    """
    if dict_sseopts:
        cfg = ConfigParser()
        cfg.read('config.ini')
        paths = cfg.get('greeks', 'greekspaths').split(',')
        for path in paths:
            with open(path + 'greeks.csv', 'wt') as f:
                f.write('underlyingprice=' + str(underlying_price) + '\n')
                for optcode, sseopt in dict_sseopts.items():
                    f.write(','.join(['code='+optcode, 'delta='+str(round(sseopt.delta, 4)),
                                      'gamma='+str(round(sseopt.gamma, 4)),
                                      'vega='+str(round(sseopt.vega, 4))]) + '\n')


def set_greeks_param():
    """
    设置计算期权希腊字母的参数，包含：无风险利率，股息率，标的波动率
    :return: 无
    """
    # 1.无风险利率=一年期shibor拆放利率
    global RISK_FREE
    # df_shibor = ts.shibor_data()    # 取得当前年份的shibor数据（dataframe格式）
    # df_shibor = df_shibor.sort_values(by='date', ascending=False).head(10)
    # RISK_FREE = float(df_shibor.iloc[0, 8])/100.0
    cfg = ConfigParser()
    cfg.read('config.ini')
    RISK_FREE = float(cfg.get('greeks', 'riskfree'))/100.0
    print('risk free = ' + str(RISK_FREE))
    # 2.股息率=0
    global DIVIDEND_RATE
    DIVIDEND_RATE = 0.0
    # 3.标的波动率=60个交易日的对数收益率计算的年化标准差
    global UNDERLYING_VOL
    str_start = (datetime.date.today() - datetime.timedelta(days=100)).strftime('%Y-%m-%d')
    str_end = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    df_underlying_k_data = ts.get_k_data('510050', start=str_start, end=str_end)
    ind1 = list(df_underlying_k_data.index.values[-61:-1])
    ind2 = list(df_underlying_k_data.index.values[-60:])
    arr_underlying_close1 = df_underlying_k_data.ix[ind1, 'close'].values
    arr_underlying_close2 = df_underlying_k_data.ix[ind2, 'close'].values
    arr_underlying_log_ret = np.log(arr_underlying_close2 / arr_underlying_close1)
    UNDERLYING_VOL = np.std(arr_underlying_log_ret) * math.sqrt(250.0)
    print('underlying vol = ' + str(UNDERLYING_VOL))


if __name__ == '__main__':
    set_greeks_param()
    CMkt = OptRtMktData()
    while True:
        print(time.strftime('%H:%M:%S', time.localtime(time.time())) + ' download opt rt mkt data and calculate opt greeks done.')
        CMkt.download_opt_rtmktdata()
        CMkt.download_underlying_rtmktdata()
        time.sleep(CMkt.interval)

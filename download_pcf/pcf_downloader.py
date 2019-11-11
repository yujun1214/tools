from configparser import ConfigParser
import requests
import datetime
import os
import re

# 从配置文件加载配置参数
cfg = ConfigParser()
cfg.read('config.ini')
pcf_file_path = cfg.get('path', 'pcf_save_path')

# ========== 下载上交所单市场、跨市场ETF的pcf文件 ==============
# 读取上交所ETF代码信息，单市场ETF的type=1，跨市场ETF的type=2
print('Downloading SSE ETF Codes...')
sse_etf_codes = {}
url = "http://query.sse.com.cn/infodisplay/queryETFNewAllInfo.do?"
params = {'isPagination': 'false', 'type': '1'}
headers = {'Host': 'query.sse.com.cn', 'Referer': 'http://www.sse.com.cn/disclosure/fund/etflist/'}
resp = requests.get(url, params=params, headers=headers)
sse_etf_codeinfo = resp.json()['pageHelp']['data']
for code_info in sse_etf_codeinfo:
    code = code_info['fundid1']
    code = code[:-1] + '0.SH'
    sse_etf_codes[code] = code_info['etftype']

params = {'isPagination': 'false', 'type': '2'}
resp = requests.get(url, params=params, headers=headers)
sse_etf_codeinfo = resp.json()['pageHelp']['data']
for code_info in sse_etf_codeinfo:
    code = code_info['fundid1']
    code = code[:-1] + '0.SH'
    sse_etf_codes[code] = code_info['etftype']

# 遍历上交所ETF代码，下载pcf文件
# pcf_file_path = '/Users/davidyujun/Dropbox/tools/download_pcf/pcf'
for sse_etf_code, sse_etf_type in sse_etf_codes.items():
    print('[%s] Downloading ETF %s...' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), sse_etf_code))
    url = "http://query.sse.com.cn/etfDownload/downloadETF2Bulletin.do?etfType=%s" % sse_etf_type
    resp = requests.get(url)
    resp.encoding = 'GBK'
    strPCFText = resp.text.replace('\r', '')
    nTradingDayPos = strPCFText.find('TradingDay')
    if nTradingDayPos > -1:
        tmPCFDate = datetime.datetime.strptime(strPCFText[nTradingDayPos+11:nTradingDayPos+19], '%Y%m%d').date()
        if tmPCFDate != datetime.date.today():
            print("PCF TradingDay of ETF %s is not available." % sse_etf_code)
        else:
            with open(os.path.join(pcf_file_path,
                                   '%s_%s.txt' % (sse_etf_code, datetime.date.today().strftime('%Y%m%d'))), 'wt') as f:
                f.write(strPCFText)
    else:
        print("PCF TradingDay of ETF %s is not available." % sse_etf_code)
# ===============================================================

# ============= 下载深交所ETF的pcf文件 ==========================
print('Downloading szse ETF Codes...')

# # szse_etf_codes = []
# # url = "http://www.szse.cn/szseWeb/ShowReport.szse?SHOWTYPE=EXCEL&CATALOGID=1945&ENCODE=1&TABKEY=tab1"
# url = "http://www.szse.cn/api/report/ShowReport?SHOWTYPE=xlsx&CATALOGID=1105&TABKEY=tab1"
# headers = {'Referer': 'http://www.szse.cn/'}
# resp = requests.get(url, headers=headers)
# resp.encoding = 'GBK'
# # pcf_file_path = '/Users/davidyujun/Dropbox/tools/download_pcf/pcf'

szse_etf_codes = []
for page_no in range(1, 10):
    url = 'http://www.szse.cn/api/report/ShowReport/data?SHOWTYPE=JSON&CATALOGID=1105&TABKEY=tab1&PAGENO=%d&selectJjlb=ETF&selectTzlb=股票基金' % page_no
    rsp = requests.get(url)
    if rsp.json()[0]['data']:
        for etf_info in rsp.json()[0]['data']:
            szse_etf_codes.append(re.match(r'.*<u>(\d{6})</u>', etf_info['sys_key']).group(1))
    else:
        break

# for szse_etf_code in re.findall(r'159\d{3}', resp.text):
for szse_etf_code in szse_etf_codes:
    print('[%s] Downloading EFT %s.SZ...' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), szse_etf_code))
    # url = "http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=downloadEtf&filename=pcf_%s_%s%%3B%sETF%s" % \
    #       (szse_etf_code, datetime.date.today().strftime('%Y%m%d'), szse_etf_code,
    #        datetime.date.today().strftime('%Y%m%d'))
    # url = "http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=downloadEtf&filename=pcf_%s_%s%%3B%sETF%s" % \
    #       (szse_etf_code, '20170928', szse_etf_code, '20170928')
    url = 'http://reportdocs.static.szse.cn/files/text/ETFDown/pcf_%s_%s.txt' % (szse_etf_code, datetime.date.today().strftime('%Y%m%d'))
    resp = requests.get(url)
    # resp.encoding = 'GBK'
    strPCFText = resp.text
    if strPCFText[:5] == '<?xml':
        resp.encoding = 'UTF-8'
        strPCFText = resp.text
        with open(os.path.join(pcf_file_path,
                               '%s.SZ_%s.xml' % (szse_etf_code, datetime.date.today().strftime('%Y%m%d'))), 'wt') as f:
            f.write(strPCFText)
    elif strPCFText[:11] == '[FILEBEGIN]':
        resp.encoding = 'GBK'
        strPCFText = resp.text.replace('\r', '')
        with open(os.path.join(pcf_file_path,
                               '%s.SZ_%s.txt' % (szse_etf_code, datetime.date.today().strftime('%Y%m%d'))), 'wt') as f:
            f.write(strPCFText)
    else:
        print('找不到%s.SZ的pcf文件' % szse_etf_code)
# ==============================================================

# ============ 从基金公司网站下载pcf文件 ===========================
print("Downloading pcf file from fund company's website...")
print("[%s] Downloading ETF 159919.SZ..." % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
url = "http://download.jsfund.cn/pcf/159919/%d/pcf_159919_%s.txt" % (datetime.date.today().year, datetime.date.today().strftime('%Y%m%d'))
resp = requests.get(url)
resp.encoding = 'GBK'
strPCFText = resp.text.replace('\r', '')
nTradingDayPos = strPCFText.find('TradingDay')
if nTradingDayPos > -1:
    tmPCFDate = datetime.datetime.strptime(strPCFText[nTradingDayPos+11:nTradingDayPos+19], '%Y%m%d').date()
    if tmPCFDate != datetime.date.today():
        print('PCF Tradingday of ETF 159919.SZ is not available.')
    else:
        with open(os.path.join(pcf_file_path,
                               '159919.SZ_%s.txt' % datetime.date.today().strftime('%Y%m%d')), 'wt') as f:
            f.write(strPCFText)
else:
    print('PCF Tradingday of ETF 159919.SZ is not available.')
# ================================================================

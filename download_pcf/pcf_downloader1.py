from configparser import ConfigParser
import requests
import datetime
import os
import re
import xml.etree.ElementTree as ET

# 从配置文件加载配置参数
cfg = ConfigParser()
cfg.read('config.ini')
pcf_file_paths = cfg.get('path', 'pcf_save_path').split(",")

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
etf_to_download = ['510360.SH', '510300.SH', '510310.SH', '510330.SH', '510500.SH', '510510.SH', '510520.SH',
                   '512500.SH', '512510.SH', '510560.SH', '510050.SH', '510710.SH', '510600.SH', '510850.SH',
				   '510350.SH', '510390.SH']
for sse_etf_code, sse_etf_type in sse_etf_codes.items():
    if sse_etf_code not in etf_to_download:
        continue
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
            for pcf_file_path in pcf_file_paths:
                with open(os.path.join(pcf_file_path,
									   '%s_%s.txt' % (sse_etf_code, datetime.date.today().strftime('%Y%m%d'))), 'wt', encoding='GBK') as f:
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
szse_etf_codes = ['159919', '159925', '159922', '159935']
for szse_etf_code in szse_etf_codes:
    print('[%s] Downloading EFT %s.SZ...' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), szse_etf_code))
    # url = "http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=downloadEtf&filename=pcf_%s_%s%%3B%sETF%s" % \
    #       (szse_etf_code, datetime.date.today().strftime('%Y%m%d'), szse_etf_code,
    #        datetime.date.today().strftime('%Y%m%d'))
    # url = "http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=downloadEtf&filename=pcf_%s_%s%%3B%sETF%s" % \
    #       (szse_etf_code, '20170928', szse_etf_code, '20170928')

    # url = 'http://reportdocs.static.szse.cn/files/text/ETFDown/pcf_%s_%s.txt' % (szse_etf_code, datetime.date.today().strftime('%Y%m%d'))
    # resp = requests.get(url)
    # # resp.encoding = 'GBK'
    # strPCFText = resp.text
    # if strPCFText[:5] == '<?xml':
    #     resp.encoding = 'UTF-8'
    #     strPCFText = resp.text
    #     for pcf_file_path in pcf_file_paths:
    #         with open(os.path.join(pcf_file_path,
    #                                '%s.SZ_%s.xml' % (szse_etf_code, datetime.date.today().strftime('%Y%m%d'))), 'wt') as f:
    #             f.write(strPCFText)
    # elif strPCFText[:11] == '[FILEBEGIN]':
    #     resp.encoding = 'GBK'
    #     strPCFText = resp.text.replace('\r', '')
    #     for pcf_file_path in pcf_file_paths:
    #         with open(os.path.join(pcf_file_path,
    #                                '%s.SZ_%s.txt' % (szse_etf_code, datetime.date.today().strftime('%Y%m%d'))), 'wt') as f:
    #             f.write(strPCFText)
    # else:
    #     print('找不到%s.SZ的pcf文件' % szse_etf_code)


    url_txt = 'http://reportdocs.static.szse.cn/files/text/ETFDown/pcf_%s_%s.txt' % (szse_etf_code, datetime.date.today().strftime('%Y%m%d'))
    url_xml = 'http://reportdocs.static.szse.cn/files/text/ETFDown/pcf_%s_%s.xml' % (szse_etf_code, datetime.date.today().strftime('%Y%m%d'))
    resp = requests.get(url_txt)
    if resp.status_code == requests.codes.ok:
        resp.encoding = 'GBK'
        strPCFText = resp.text.replace('\r', '')
        for pcf_file_path in pcf_file_paths:
            with open(os.path.join(pcf_file_path,
                                   '%s.SZ_%s.txt' % (szse_etf_code, datetime.date.today().strftime('%Y%m%d'))),
                      'wt', encoding='GBK') as f:
                f.write(strPCFText)
    else:
        resp = requests.get(url_xml)
        if resp.status_code == requests.codes.ok:
            resp.encoding = 'UTF-8'
            strPCFText = resp.text
            xml_root = ET.fromstring(strPCFText)
            str_namespace = '{http://ts.szse.cn/Fund}'
            for pcf_file_path in pcf_file_paths:
                with open(os.path.join(pcf_file_path,
                                       '%s.SZ_%s.txt' % (szse_etf_code, datetime.date.today().strftime('%Y%m%d'))),
                          'wt', encoding='GBK') as f:
                    strlines = ['[FILEBEGIN]\n']
                    # for chd_item in xml_root:
                    #     if chd_item.tag != '%sComponents' % str_namespace:
                    #         strline = '%s=%s\r\n' % (chd_item.tag[len(str_namespace):], chd_item.text)
                    #         f.write(strline)
                    #     else:
                    #         for chd_comp in chd_item:
                    #             if chd_comp.tag == 'Component':
                    #                 for secu_item in chd_comp:
                    #                     strline = '%s=%s' % (secu_item.tag[len(str_namespace):], secu_item.text)
                    #                     f.write(strline)

                    strlines.append('Version=%s\n' % xml_root.find(str_namespace + 'Version').text)
                    strlines.append('FundID=%s\n' % xml_root.find(str_namespace + 'SecurityID').text)
                    strlines.append('FundName=%s\n' % xml_root.find(str_namespace + 'Symbol').text)
                    strlines.append('FundManagementCompany=%s\n' % xml_root.find(str_namespace + 'FundManagementCompany').text)
                    strlines.append('UnderlyingIndex=%s\n' % xml_root.find(str_namespace + 'UnderlyingSecurityID').text)
                    strlines.append('CreationRedemptionUnit=%s\n' % xml_root.find(str_namespace + 'CreationRedemptionUnit').text)
                    strlines.append('EstimateCashComponent=%s\n' % xml_root.find(str_namespace + 'EstimateCashComponent').text)
                    strlines.append('MaxCashRatio=%s\n' % xml_root.find(str_namespace + 'MaxCashRatio').text)
                    strlines.append('Publish=%s\n' % xml_root.find(str_namespace + 'Publish').text)
                    strlines.append('Creation=%s\n' % xml_root.find(str_namespace + 'Creation').text)
                    strlines.append('Redemption=%s\n' % xml_root.find(str_namespace + 'Redemption').text)
                    strlines.append('TotalRecordNum=%s\n' % xml_root.find(str_namespace + 'TotalRecordNum').text)
                    strlines.append('TradingDay=%s\n' % xml_root.find(str_namespace + 'TradingDay').text)
                    strlines.append('PreTradingDay=%s\n' % xml_root.find(str_namespace + 'PreTradingDay').text)
                    strlines.append('CashComponent=%s\n' % xml_root.find(str_namespace + 'CashComponent').text)
                    strlines.append('NAVperCU=%s\n' % xml_root.find(str_namespace + 'NAVperCU').text)
                    strlines.append('NAV=%s\n' % xml_root.find(str_namespace + 'NAV').text)
                    strlines.append('DividendPerCU=%s\n' % xml_root.find(str_namespace + 'DividendPerCU').text)
                    strlines.append('CreationLimit=%s\n' % xml_root.find(str_namespace + 'CreationLimit').text)
                    strlines.append('RedemptionLimit=%s\n' % xml_root.find(str_namespace + 'RedemptionLimit').text)

                    strlines.append('[RECORDBEGIN]\n')
                    for secu_comp in xml_root.find(str_namespace + 'Components').findall(str_namespace + 'Component'):
                        strSecuCode = secu_comp.find(str_namespace + 'UnderlyingSecurityID').text
                        strSecuName = secu_comp.find(str_namespace + 'UnderlyingSymbol').text
                        if strSecuName == '申赎现金':
                            continue
                        strSecuName = strSecuName.ljust(26)
                        strVol = secu_comp.find(str_namespace + 'ComponentShare').text.rjust(8)
                        strSubstituteFlag = secu_comp.find(str_namespace + 'SubstituteFlag').text
                        strPremiumRatio = secu_comp.find(str_namespace + 'PremiumRatio').text.rjust(8)
                        strCreationCash = secu_comp.find(str_namespace + 'CreationCashSubstitute').text
                        strCreationCash = ' ' * 16 if int(eval(strCreationCash)) == 0 else strCreationCash.rjust(16)
                        strRedemptionCash = secu_comp.find(str_namespace + 'RedemptionCashSubstitute').text
                        strRedemptionCash = ' ' * 16 if int(eval(strRedemptionCash)) == 0 else strRedemptionCash.rjust(16)
                        if strSecuCode[0] == '6':
                            strExchangeFlag = '1'
                            strExchangeName = 'XSHG    '
                        else:
                            strExchangeFlag = '0'
                            strExchangeName = 'XSHE    '

                        strSecuCompLine = '%s|%s|%s|%s|%s|%s|%s|%s|%s|\n' % (strExchangeFlag, strSecuCode, strSecuName, strVol, strSubstituteFlag, strPremiumRatio, strCreationCash, strRedemptionCash, strExchangeName)
                        strlines.append(strSecuCompLine)

                    strlines.append('[RECORDEND]\n')
                    strlines.append('[FILEEND]\n')

                    f.writelines(strlines)
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
        for pcf_file_path in pcf_file_paths:
            with open(os.path.join(pcf_file_path,
                                   '159919.SZ_%s.txt' % datetime.date.today().strftime('%Y%m%d')), 'wt', encoding='GBK') as f:
                f.write(strPCFText)
else:
    print('PCF Tradingday of ETF 159919.SZ is not available.')
# ================================================================

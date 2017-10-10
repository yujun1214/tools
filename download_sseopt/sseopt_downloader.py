from configparser import ConfigParser
import requests
import datetime
import os

# 从配置文件加载配置参数
cfg = ConfigParser()
cfg.read('config.ini')
opt_file_path = cfg.get('path', 'optdata_save_path')

# 下载上交所期权“当日合约”文件
print('Download SSE option data at %s' % datetime.date.today().strftime('%Y-%m-%d'))
url = "http://query.sse.com.cn/commonQuery.do?"
params = {'isPagination': 'true', 'expireDate': '', 'securityId': '510050',
          'sqlId': 'SSE_ZQPZ_YSP_GGQQZSXT_XXPL_DRHY_SEARCH_L', 'pageHelp.pageSize': '10000',
          'pageHelp.pageNo': '1', 'pageHelp.beginPage': '1', 'pageHelp.cacheSize': '1',
          'pageHelp.endPage': '5'}
headers = {'Host': 'query.sse.com.cn', 'Referer': 'http://www.sse.com.cn/assortment/options/disclo/preinfo/'}
resp = requests.get(url, params=params, headers=headers)
sseopts = resp.json()['pageHelp']['data']

with open(os.path.join(opt_file_path, 'SSEOptContract%s.txt' % datetime.date.today().strftime('%Y%m%d')), 'wt') as f:
    for sseopt in sseopts:
        opt_one_line = '|'.join([key + '=' + value for key, value in sseopt.items()])
        f.write(opt_one_line + '\n')

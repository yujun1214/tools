import requests
import datetime

url = "http://query.sse.com.cn/commonQuery.do?"
params = {'isPagination': 'true', 'expireDate': '', 'securityId': '510050',
          'sqlId': 'SSE_ZQPZ_YSP_GGQQZSXT_XXPL_DRHY_SEARCH_L', 'pageHelp.pageSize': '10000',
          'pageHelp.pageNo': '1', 'pageHelp.beginPage': '1', 'pageHelp.cacheSize': '1',
          'pageHelp.endPage': '5'}
headers = {'Host': 'query.sse.com.cn', 'Referer': 'http://www.sse.com.cn/assortment/options/disclo/preinfo/'}
resp = requests.get(url, params=params, headers=headers)
sseopts = resp.json()['pageHelp']['data']

with open('SSEOptContract' + datetime.date.today().strftime('%Y%m%d') + '.txt', 'wt') as f:
    for sseopt in sseopts:
        one_opt_line = '|'.join([key + '=' + value for key, value in sseopt.items()])
        f.write(one_opt_line + '\n')
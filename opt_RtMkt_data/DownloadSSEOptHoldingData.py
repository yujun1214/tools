import requests
import datetime

strBegDate = '20170101'
strEndDate = '20170816'
url = "http://query.sse.com.cn/commonQuery.do?"
headers = {'Host': 'query.sse.com.cn', 'Referer': 'http://www.sse.com.cn/assortment/options/date/'}

tmTradingDay = datetime.datetime.strptime(strBegDate, '%Y%m%d')
tmEndDay = datetime.datetime.strptime(strEndDate, '%Y%m%d')
while tmTradingDay <= tmEndDay:
    # download daily statistical data of SSE options
    params = {'isPagination': True, 'sqlId': 'COMMON_SSE_ZQPZ_YSP_QQ_SJTJ_MRTJ_CX',
              'tradeDate': tmTradingDay.strftime('%Y%m%d'),
              'pageHelp.pageSize': '5', 'pageHelp.pageNo': '1', 'pageHelp.beginPage': '1',
              'pageHelp.cacheSize': '1', 'pageHelp.endPage': '5'}
    resp = requests.get(url, params=params, headers=headers)
    daily_stats = resp.json()['result']
    if len(daily_stats) > 0:
        print('Downloading SSE daily options data of ' + tmTradingDay.strftime('%Y%m%d'))
        with open('SSEOptDailyStats' + tmTradingDay.strftime('%Y%m%d') + '.txt', 'wt') as f:
            for stat_data in daily_stats:
                one_stat_line = ','.join([key + '=' + value for key, value in stat_data.items()])
                f.write(one_stat_line)

    # download monthly statistical data of SSE option
    tmPreDay = tmTradingDay - datetime.timedelta(days=1)
    if tmPreDay.month != tmTradingDay.month:
        params = {'isPagination': True, 'sqlId': 'COMMON_SSE_ZQPZ_YSP_QQ_SJTJ_YDTJ_CX',
                  'tradeDate': tmPreDay.strftime('%Y%m'),
                  'pageHelp.pageSize': '10', 'pageHelp.pageNo': '1', 'pageHelp.beginPage': '1',
                  'pageHelp.cacheSize': '1', 'pageHelp.endPage': '5'}
        resp = requests.get(url, params=params, headers=headers)
        monthly_stats = resp.json()['result']
        if len(monthly_stats) > 0:
            print('Downloading SSE monthly options data of ' + tmPreDay.strftime('%Y%m'))
            with open('SSEOptMonthlyStats' +  tmPreDay.strftime('%Y%m') + '.txt', 'wt') as f:
                for stat_data in monthly_stats:
                    one_stat_line = ','.join([key + '=' + value for key, value in stat_data.items()])
                    f.write(one_stat_line)
    tmTradingDay += datetime.timedelta(days=1)


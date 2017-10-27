from configparser import ConfigParser
import requests
import datetime
import os

# 以下为用STMP发送邮件添加的引用
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import parseaddr, formataddr
from email.mime.base import MIMEBase
import smtplib

# 从配置文件加载配置参数
cfg = ConfigParser()
cfg.read('config.ini')
opt_file_path = cfg.get('path', 'optdata_save_path')

# 以下是发送邮件相关函数
def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

def send_sseopt_file():
    # 邮件对象
    msg = MIMEMultipart()
    msg['From'] = _format_addr('余君 <yujun_mail@163.com>')
    msg['From'] = 'yujun_mail@163.com'
    msg['To'] = _format_addr('余君 <yujun_mail@163.com,yujun_mail@sina.com>')
    msg['Subject'] = Header('上交所股票期权当日合约文件', 'utf-8').encode()

    # 邮件正文是MIMEText
    msg.attach(MIMEText('请查收', 'plain', 'utf-8'))

    # 添加附件（即加上一个MIMEBase）
    attached_file_name = os.path.join(opt_file_path, 'SSEOptContract%s.txt' % datetime.date.today().strftime('%Y%m%d'))
    with open(attached_file_name, 'r') as f:
        mime = MIMEBase('application', 'octet-stream', filename=os.path.basename(attached_file_name))
        mime.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attached_file_name))
        mime.add_header('Content-ID', '<0>')
        mime.add_header('X-Attachment-Id', '0')
        mime.set_payload(f.read(), charset='utf-8')
        encoders.encode_base64(mime)
        msg.attach(mime)

        # mime = MIMEText(f.read(), 'base64', 'utf-8')
        # mime['Content-Type'] = 'application/octet-stream'
        # mime['Content-Disposition'] = 'attachment;filename="%s"' % os.path.basename(attached_file_name)
        # msg.attach(mime)

    server = smtplib.SMTP('smtp.163.com')
    # server.set_debuglevel(1)
    server.login('yujun_mail@163.com', 'icbccs_791025')
    server.sendmail('yujun_mail@163.com', ['yujun_mail@sina.com', 'yujun_mail@163.com'], msg.as_string())
    server.quit()

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

with open(os.path.join(opt_file_path, 'SSEOptContract%s.txt' % datetime.date.today().strftime('%Y%m%d')), 'wt', newline='\n') as f:
    for sseopt in sseopts:
        opt_one_line = '|'.join([key + '=' + value for key, value in sseopt.items()])
        f.write(opt_one_line + '\n')

# 发送邮件
send_sseopt_file()

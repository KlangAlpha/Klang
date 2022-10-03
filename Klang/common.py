
import argparse
from datetime import datetime
import time
parser = argparse.ArgumentParser()
parser.add_argument("--offset", help="开始执行的位置",default='0')
parser.add_argument("--end", help="日期",default='0')
parser.add_argument("--start", help="日期",default='2020-10-01')

args = parser.parse_known_args()
if len(args) > 1:
    args = args[0]

end = args.end
start = args.start

def gettoday():
    today = datetime.now()
    return str(today.year) + '-' +str(today.month) +'-'+ str(today.day)

if end== '0':
    end = gettoday()

#
# day = 0 ,获取今天的 日期 2022-05-xx
# day = 1 ,获取昨天的 日期 
# day = N ,获取N天之前的日期

def get_date(day):
    now = int(time.time())
    now = now - day * 24 * 3600 #往前N天
    timeArray = time.localtime(now)
    return time.strftime("%Y-%m-%d", timeArray)

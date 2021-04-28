import requests
import re
import os
import pandas as pd

import argparse
import time
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("--offset", help="开始执行的位置",default='0')
parser.add_argument("--end", help="日期",default='0')
parser.add_argument("--start", help="日期",default='2020-01-01')

args = parser.parse_args()

end = args.end
start = args.start

today = datetime.now()
if end== '0':
    end = str(today.year) + '-' +str(today.month) +'-'+ str(today.day)


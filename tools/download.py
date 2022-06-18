#
# 通过文件下载日K
#

import zipfile
import requests
from progress import bar
import os,shutil

bar.Bar.suffix = bar.ChargingBar.suffix +" " + bar.Bar.suffix
bar.Bar.color = bar.color('blue')


host = "https://klang.org.cn/"
filename = "stockdata.zip"
url = host + filename
filename_jsont = os.path.expanduser("~/.klang_stock_trader.json")


def download():

    resp = requests.head(url)
    filelength = int(resp.headers.get('Content-Length', -1))

    prog = bar.Bar('Downloading ' + filename, max=filelength)

    req = requests.get(url, stream=True)

    try:
        with(open(filename, 'ab')) as f:
            for chunk in req.iter_content(chunk_size=1024*100):
                if chunk:
                    f.write(chunk)
                    prog.next(1024 * 100)
    except Exception as e:
        print(e)
        return False
    prog.finish()

def unzip():
    zf = zipfile.ZipFile(filename)
    for name in zf.namelist():
        print("unzip ",name)
        zf.extract(name)
    zf.close()

# step 1. download file
download()

# step 2. unzip file

unzip()


# step 3. remove 

shutil.move('.klang_stock_trader.json',filename_jsont)

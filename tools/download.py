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
def get_path(name):
    t = os.path.expanduser(name)
    return os.path.normpath(t)

data_path = get_path("~/.klang")
os.makedirs(data_path, exist_ok=True)
dst_path = data_path
temp_zipfile = get_path("~/"+filename)

def download():

    resp = requests.head(url)
    filelength = int(resp.headers.get('Content-Length', -1))
    
    prog = bar.Bar('Downloading ' + filename, max=filelength)
    prog.is_tty = lambda : True
    req = requests.get(url, stream=True)

    try:
        with(open(temp_zipfile, 'ab')) as f:
            for chunk in req.iter_content(chunk_size=1024*100):
                if chunk:
                    f.write(chunk)
                    prog.next(1024 * 100)
    except Exception as e:
        print(e)
        return False
    prog.finish()

def unzip():
    with zipfile.ZipFile(temp_zipfile,"r") as zipObj:
        zipObj.extractall(dst_path)
# step 1. download file
download()

# step 2. unzip file

unzip()


# step 3. remove 
os.remove(temp_zipfile)

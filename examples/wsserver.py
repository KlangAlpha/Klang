#!/usr/bin/env python

# WS server example that synchronizes state across clients

import asyncio
import json
import logging
import websockets
from threading import Lock
logging.basicConfig()

import threading

######################klang #######################
from Klang.lang import kparser,setPY,Kexec

from Klang import (Kl,
    OPEN, O,
    HIGH, H,
    LOW, L,
    CLOSE, C,
    VOLUME, V, VOL,
    DATETIME,

    SMA,MA,EMA,WMA,

    SUM,ABS,STD,

    CROSS,
    REF,BARSLAST,BARSCOUNT,BARSLASTFIND,
    MAX,
    MIN,
    EVERY,
    COUNT,
    HHV,
    LLV,
    IF, IIF,
    MACD,APPROX)

code = Kl.code
date = Kl.date


def getpyglobals(name):
    return globals().get(name)

def setpyglobals(name,val):
    globals()[name]=val


setPY(getpyglobals,setpyglobals)

def getstockinfo(name=0):
    return Kl.currentdf['name'], Kl.currentdf['code'],\
            Kl.currentdf['df']['hqltsz'].iloc[-1],\
            Kl.currentdf['tdxbk'],\
            Kl.currentdf['tdxgn']
 

def kloopexec(webindex,content):
    code = "webindex =" + str(webindex) + "\n"
    code += "kloop \n" + content + "\nendp;"
    return code

def cmd_call(data):
    code = data['content']
    pw   = data['pw']
    if code == "reset_all" and pw == "Klang":
        #Kl.updateall()
        t = threading.Thread(target=Kl.updateall)
        t.start()
    if code == "reset_stock"  and pw == "Klang" :
        #异步加载df 放到df_all
        t = threading.Thread(target=Kl.updatestockdata)
        t.start()

###################web socket######################
USERS = {}
index = 0
busy = 0
mutex = Lock ()
current = 0 # default display user

def await_run(coroutine):
    try:
        coroutine.send(None)
    except StopIteration as e:
        return e.value

# 因为DISPLAY是需要在Klang执行，所以需要await_run执行 sync消息
def DISPLAY(value):
    name,code,hqltsz,tdxbk,tdxgn = getstockinfo()
    message = {"type":"display","name":name,"code":code,\
        "value":str(value),"hqltsz":hqltsz,'tdxbk':tdxbk,'tdxgn':tdxgn}
    msg = json.dumps(message)
    await_run(USERS[current].send(msg))

def users_event():
    return json.dumps({"type": "users", "count": len(USERS),"busy":busy})


async def notify_users():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = users_event()
        await asyncio.wait([USERS[user].send(message) for user in USERS])

async def notice(message):
    msg = json.dumps(message)
    await asyncio.wait([USERS[user].send(msg) for user in USERS])

mutexuser = Lock ()

async def register(websocket):
    global USERS,index
    mutexuser.acquire()
    USERS[index] = websocket
    index += 1 
    mutexuser.release()
    await notify_users()
    return index - 1

async def unregister(index):
    mutexuser.acquire()
    if USERS.get(index,None) != None:
        del USERS[index]
    mutexuser.release()
    await notify_users()


async def execute(data,webindex):
    global busy,current
    print(data)
    # 1. 判断是否在执行中
    if busy == 1: #同时只能有一人之行
        await notice({"type":"busy","value":True,"op" :False})
        return

    # 2. 判断是否加loop循环之行
    if data.get("loop") is not None:
        code = kloopexec(webindex,data['content'])
    else:
        code = "webindex="+str(webindex)+"\n" + data['content']+"\n"

    # 3. 执行 busy lock 执行锁
    mutex.acquire()

    current = webindex
    busy = 1
    await notice({"type":"busy","value":True})
    Kexec(code)
    # unlock

    mutex.release()   #之行完成，解锁，发通知给web用户
    print('执行完成')

    # 4. 执行完成 
    await notice({"type":"busy","value":False})
    current = 0
    busy = 0



async def counter(websocket, path):
    # register(websocket) sends user_event() to websocket
    global busy,current
    webindex = await register(websocket) #webindex is fixed name,use by *.html
    print("register ",webindex,USERS)
    try:
        async for message in websocket:
            data = json.loads(message)
            if data["action"] == "execute":
                await execute(data,webindex)

            if data["action"] == "cmd":
                cmd_call(data)     
    except:
        if current == webindex:
            current = 0
            busy = 0
        await unregister(webindex)
    finally:
        await unregister(webindex)
        
start_server = websockets.serve(counter, "0.0.0.0", 9099)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

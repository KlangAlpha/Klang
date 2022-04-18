#!/usr/bin/env python

# klang WS server 管理程序 that synchronizes state across clients

import asyncio
import json
import logging
import websockets
from threading import Lock,Thread
logging.basicConfig()

import threading
import sys 

if len(sys.argv) > 1:
    port = int(sys.argv[1])
else:
    port = 9099

###################web socket######################
# 服务器列表
server_list=[
]
#服务器和用户对应表
server_user={

}

#用户列表
USERS = {}

#msg format
msg = {
    "type"    :"",
    "content" :{
        "value": "",
    },
}

mutex = Lock ()
mutexsu = Lock () #server and user 操作

# server 和klang执行服务器交互
# Klang msg type
#K_REG          = "K_REG"   #服务器发送给管理这服务器上线
#K_UNREG        = "K_UNREG" #服务器发送给管理者服务器离开
K_HEARTBEAT    = "K_HEART" #心跳包 
K_EXE          = "K_EXE"  #管理者发送给服务器
K_DONE         = "K_DONE" #服务器返回给管理者
K_CMD          = "K_CMD"  #管理者发送给服务器
K_RET          = "K_RET"  #服务器返回给管理者

class KlangMSG():
    def __init__(self):
        pass
    def pack(self):
        pass
    def unpack(self):
        pass
    def recv(self):
        pass
    def send(self):
        pass
    def server_increase(self,websocket):
        mutexsu.acquire()
        mutexsu.release()
    def server_decrease(self):
        mutexsu.acquire()
        mutexsu.release()
#
# 浏览器用户和管理者交互
#
# USER msg type
# U_REG     = "U_REG"   #用户发给管理者，用户上线
# U_UNREG   = "U_UNREG" #用户发给管理者，用户掉线
U_EXE     = "U_EXE"   #用户发给管理者，用户要执行代码
U_CMD     = "U_CMD"   #用户发给管理者，要更新数据
U_RET     = "U_RET"   #服务器发给用户，执行的结果
U_INFO    = "U_INFO"  #服务器发给用户，用户信息和服务器信息

class UserMSG():
    def __init__(self):
        pass
    def pack(self):
        pass
    def unpack(self):
        pass
    def recv(self):
        pass
    def send(self):
        pass
    def user_increase(self,websocket):
        mutexsu.acquire()
        mutexsu.release()

    def use_decrease(self):
        mutexsu.acquire()
        mutexsu.release()

index = 0
busy  = 0
current = 0 # default display user

def await_run(coroutine):
    try:
        coroutine.send(None)
    except StopIteration as e:
        return e.value

# 因为DISPLAY是需要在Klang执行，所以需要await_run执行 sync消息
def DISPLAY(value):
    name,code,hqltsz,tdxbk,tdxgn = getstockinfo()
    chouma = Kl.chouma()
    message = {"type":"display","name":name,"code":code,\
        "value":str(value),"hqltsz":hqltsz,'tdxbk':tdxbk,'tdxgn':tdxgn,'chouma':chouma}
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


async def register(websocket):
    global USERS,index
    mutexuser.acquire()
    USERS[index] = websocket
    index += 1 
    mutexuser.release()
    await notify_users()
    return index - 1

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



async def listen(websocket, path):

    if (path == "/" or path ==  "/user"):
        websocket.handler = UserMSG()
        websocket.handler.user_increase(websocket)
    if (path == "/klang"): 
        websocket.handler = KlangMSG()
        websocket.handler.server_increase(websocket)

    # send msg to all USERS
    # send_notices()

    # 新链接
    while True:
        data = await websocket.recv()
        msg = json.loads(data)
        
        if msg.type == K_EXE:
            pass
        if msg.type == K_DONE:
            pass

        await websocket.send(greeting)
        websocket.handler.print(f"> {greeting}")

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

#data = asyncio.wait_for(s.recv(), timeout=10)

start_server = websockets.serve(listen, "0.0.0.0", port)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()



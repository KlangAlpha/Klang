#!/usr/bin/env python

# klang WS server 管理程序 that synchronizes state across clients

import asyncio
import json
import logging
import websockets
import socket
import traceback
from threading import Lock,Thread
logging.basicConfig()

import threading
import sys,time,os 

# K WS manager 9088
# nginx ws 8099 -> 9088
# nginx wss 9099 -> 9088

if len(sys.argv) > 1:
    port = int(sys.argv[1])
else:
    port = 9088 # nginx 9099-> 9088


def PrintException():
    import linecache
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

###################web socket######################
# 服务器列表
# 0, 默认的，老的选股
# 1, 回测
# 2, 选股
##############################
server_list = {
    0:[],
    1:[],
    2:[],        
}

#用户列表
user_list=[]

mutex = Lock ()
mutexsu = Lock () #server and user 操作

# server 和klang执行服务器交互
# Klang msg type
K_HEARTBEAT    = "K_HEART" #心跳包 
K_EXE          = "K_EXE"  #管理者发送给服务器
K_DONE         = "K_DONE" #服务器返回给管理者
K_CMD          = "K_CMD"  #管理者发送给服务器
K_RET          = "K_RET"  #服务器返回给管理者

class KlangMSG():
    def __init__(self,websocket):
        self.websocket = websocket
        self.state = 0 #空闲的

    async def pack_exe(self,exe):
        msg = {
            "type":"K_EXE"
        }
        msg.update(exe)
        data = json.dumps(msg)
        await self.websocket.send(data)

    def pack_cmd(self,cmd):
        msg = {
            "type":"K_CMD"
        }
        msg.update(cmd)
        data = json.dumps(msg)
        self.websocket.send(data)
    
 
    async def parse(self,msg):
        if msg["type"] == K_RET:
            msg["type"] = U_RET
            data = json.dumps(msg)
            await self.exe_user.send(data) #转发给用户

        if msg["type"] == K_DONE:
                        
            #await self.exe_user.handler.done()
            mutex.acquire()
            self.state = 0
            self.exe_user = None
            mutex.release()
            if msg['loop'] != False:
                await send_notices()

        if msg["type"] == "LOOP_EXE":
            #获取用户websocket
            #同时释放本服务器任务
            ws_user = self.exe_user
            
            mutex.acquire()
            self.state = 0
            self.exe_user = None
            mutex.release()
            await send_notices()
            t = threading.Thread(target=do_loop,args=(msg,ws_user))
            t.start()

    def list_increase(self,stype=0):
        self.stype = stype
        mutexsu.acquire()
        server_list[stype].append(self.websocket)
        mutexsu.release()

    def list_decrease(self):
        mutexsu.acquire()
        if self.websocket in server_list[self.stype]:
            server_list[self.stype].remove(self.websocket)
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
U_DONE    = "U_DONE"  #服务器发给用户，用户执行完成

class UserMSG():
    def __init__(self,websocket):
        self.websocket = websocket
    async def pack_info(self,info):
        msg = {
            "type":"U_INFO"
        }
        msg.update(info)
        data = json.dumps(msg)
        self.websocket.send(data)

    async def pack_ret(self,ret):
        msg = {
            "type":"U_RET",
        }
        msg.update(ret)
        data = json.dumps(msg)
        await self.websocket.send(data)

    async def done(self):
        msg = {
            "type":"U_DONE",
        }
        data = json.dumps(msg)
        await self.websocket.send(data)

    async def parse(self,msg):
        if msg["type"] == U_EXE:
            stype = msg.get("stype",0)

            #
            # 1.） 查找服务器数量
            #
            if find_server_count(stype) == 0 :
                busy_msg = {"type":U_RET,"retcode":"ERROR","errmsg":"没有请求类型的服务器"}
                data = json.dumps(busy_msg)
                await self.websocket.send(data)


            mutex.acquire()

            #
            # 2.) 获取执行类型
            #
            isloop = msg.get('loop')

            ws = find_server(stype)
            if ws is None:
                busy_msg = {"type":U_RET,"retcode":"ERROR","errmsg":"没有请求类型的服务器"}
                data = json.dumps(busy_msg)
                await self.websocket.send(data)
                return

            if isloop : #等待返回code列表后，再次执行任务
                ws.handler.exe_user = self.websocket
                msg["type"] = K_EXE
                msg["event"] = "GET_BASE_LIST"
                msg["loop"]  = False # 不再让kserver处理循环，由mangager处理循环
                ws.handler.state = 1  
                await send_notices()              
                await ws.handler.pack_exe(msg)
                
            else: # 立即执行 

                ws.handler.exe_user = self.websocket
                msg["type"]=K_EXE
                msg["event"] = "DO"
                ws.handler.state = 1  
                await send_notices()              
                await ws.handler.pack_exe(msg)
            mutex.release()

        if msg["type"] == U_CMD:
            msg["type"] = K_CMD
            await updateall(msg)

    def list_increase(self):
        mutexsu.acquire()
        user_list.append(self.websocket)
        mutexsu.release()

    def list_decrease(self):
        mutexsu.acquire()
        if self.websocket in user_list:
            user_list.remove(self.websocket)
        mutexsu.release()

def await_run(coroutine):
    try:
        coroutine.send(None)
    except StopIteration as e:
        return e.value

def await_flush():
    # Windows 平台需要使用 run_once刷新要发送的数据，否则堆积发送数据直到下一个loop run发生
    if sys.platform == 'win32':
        try:
            loop = asyncio.get_running_loop()
            loop._run_once()
        except:
            pass



def do_loop(msg,ws_user):

    stype = msg.get("stype",0)
    stocklist = msg["stocklist"]
    del msg["stocklist"]
    content = msg["content"]
    for stock in stocklist:
        ws = find_server(stype) #没有服务器，任务终止
        if ws is None:
            await_run(ws_user.handler.done())
            await_flush()
            return

        source_code = "code('" + stock["code"] + "')\n;" + content
        msg ["content"] = source_code
        ws.handler.exe_user = ws_user
        msg["type"] = K_EXE
        msg["event"] = "DO"
        ws.handler.state = 1
        await_run(ws.handler.pack_exe(msg))
        await_flush()

    await_run(ws_user.handler.done())
    await_flush()

async def updateall(msg):
    data = json.dumps(msg)
    for s in server_list[msg["stype"]]:
        try:
            await s.send(data)
        except:
            pass

async def send_notices():
    server_state = []
    for key in server_list.keys() :
        for s in server_list[key]:
            server_state.append(s.handler.state)
    msg = json.dumps({
        "type":U_INFO,
        "servers":server_state,
        "users":len(user_list),
    })
    for user in user_list:
        try:
            await user.send(msg)
        except:
            print("Use send failed remove from list")
            user.handler.list_decrease()

def find_server(stype):

    while True:
        server_count = find_server_count(stype)
        if server_count == 0:
            return None

        server = server_list[stype]
        for w in server:
            if w.handler.state == 0:
                return w

        # 1 ms 等待服务器完成任务
        time.sleep(0.001)

def find_server_count(stype):
    server = server_list[stype]
    return len(server)

async def listen(websocket, path):

    if (path == "/" or path ==  "/user"):
        print("A new user connect",websocket.remote_address)
        websocket.handler = UserMSG(websocket)
        websocket.handler.list_increase()
    if (path == "/klang"): 
        print("A new server connect",websocket.remote_address)
        websocket.handler = KlangMSG(websocket)
        websocket.handler.list_increase(0)

    if (path == "/kbtserver"): 
        print("A backtest server connect",websocket.remote_address)
        websocket.handler.list_increase(1)


    # send msg to all USERS
    await send_notices()

    # 新链接
    try:
        async for data in websocket: 
            msg = json.loads(data)
            if msg["type"] not in  [K_RET ,"LOOP_EXE",K_DONE]:
                print(msg)
            await websocket.handler.parse(msg)        
    except Exception as e:
        websocket.handler.list_decrease()
        PrintException()
        print(e)
        traceback.print_stack()
    finally:
        websocket.handler.list_decrease()
        

#data = asyncio.wait_for(s.recv(), timeout=10)
async def main():

    print("Websocket manager start port:",port)
    async with websockets.serve(listen, "0.0.0.0", port,ping_interval=5000,ping_timeout=5000) as s:
        for sock in s.server.sockets:
            sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        await asyncio.Future()

asyncio.run(main())



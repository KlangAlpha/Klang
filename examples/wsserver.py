#!/usr/bin/env python

# WS server example that synchronizes state across clients

import asyncio
import json
import logging
import websockets
logging.basicConfig()


######################klang #######################
from Klang.lang import kparser,setPY,Kexec
from Klang.common import today
from Klang import Kl,C,MA,CROSS

#
# today 
#

def getpyglobals(name):
    return globals().get(name)

def setpyglobals(name,val):
    globals()[name]=val


setPY(getpyglobals,setpyglobals)

def getstockinfo():
    return Kl.currentdf['name'], Kl.currentdf['code']
 

def kloopexec(webindex,content):
    code = "webindex =" + str(webindex) + "\n"
    code += "kloop \n" + content + "\nendp;"
    return code

def cmd_call(code):
    if code == "reset_list":
        pass
    if code == "reload_stock":
        pass

###################web socket######################
USERS = {}
index = 0

def await_run(coroutine):
    try:
        coroutine.send(None)
    except StopIteration as e:
        return e.value

def DISPLAY(webindex,value):
    name,code = getstockinfo()
    message = {"type":"display","name":name,"code":code,"value":value}
    msg = json.dumps(message)
    await_run(USERS[webindex].send(msg))

def users_event():
    return json.dumps({"type": "users", "count": len(USERS)})


async def notify_users():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = users_event()
        await asyncio.wait([USERS[user].send(message) for user in USERS])


async def register(websocket):
    global USERS,index
    USERS[index] = websocket
    index += 1 
    await notify_users()
    return index - 1

async def unregister(index):
    del USERS[index]
    await notify_users()


async def counter(websocket, path):
    # register(websocket) sends user_event() to websocket
    webindex = await register(websocket) #webindex is fixed name,use by *.html
    print("register ",webindex,USERS)
    try:
        async for message in websocket:
            data = json.loads(message)
            if data["action"] == "execute":
                if data.get("loop") is not None:
                    code = kloopexec(webindex,data['content'])
                else:
                    code = "webindex="+str(webindex)+"\n" + data['content']+"\n"

                Kexec(code)
            if data["action"] == "cmd":
                    code = data['content']
                    cmd_call(code)        
    finally:
        await unregister(webindex)

start_server = websockets.serve(counter, "localhost", 6789)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

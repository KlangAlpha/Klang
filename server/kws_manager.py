import socketio
import eventlet
from threading import Lock,Thread
import threading
import sys,time,os
import json

# K WS manager 9088
# nginx ws 8099 -> 9088
# nginx wss 9099 -> 9088


# create a Socket.IO server
sio = socketio.Server( cors_allowed_origins='*' )
# wrap with a WSGI application
app = socketio.WSGIApp(sio)

mutex = Lock ()
port = 9088
server_list = {}
user_list = []

def get_server():
    if len(server_list.keys()) < 1:
        return None
    while True:
        eventlet.sleep(0.001)
        mutex.acquire()
        for s in server_list.keys():
            if server_list[s] == 0:
                server_list[s] = 1
                mutex.release()
                return s
        mutex.release()

def do_loop(data):
        stocklist = data["stocklist"]
        del data["stocklist"]
        content = data["content"]
        user_id = data["user_id"]
        
        for i in range(0,len(stocklist),20):
            new_stock_list = stocklist[i:i+20]

            ws = get_server() #没有服务器，任务终止
            if ws is None:
                self.emit('u_done',{"retcode":"没有服务器终止"},to=user_id,namespace="/user")

            
            data ['stocklist'] = new_stock_list
            
            sio.emit("do_exec",data,to=ws,namespace="/Kserver")
            
        sio.emit('u_done',{"done":"ok"},to=user_id,namespace="/user")

class Kserver(socketio.Namespace):
    def on_connect(self,sid,environ):
        print("A new server connect ",sid)
        server_list[sid] = 0
        send_notices()

    def on_disconnect(self,sid):
        del server_list[sid]
        send_notices()

    def on_ret_loop_list(self,sid,data):

        server_list[sid] = 0
        sio.start_background_task(do_loop,data)

    def on_exec_done(self,sid,data):
        #lock
        server_list[sid] = 0

    def on_user_ret(self,sid,data):
        self.emit('u_ret',data,to=data["user_id"],namespace="/user")


def send_notices():
    server_state = []
    for key in server_list.keys() :
            server_state.append(server_list[key])
    msg = {
        "servers":server_state,
        "users":len(user_list),
    }
    for user in user_list:
        sio.emit("u_info",msg,to=user,namespace="/user")


class User(socketio.Namespace):
    def on_connect(self,sid,environ):
        print("A new user connect ",sid)
        user_list.append(sid)
        send_notices()
    def on_disconnect(self,sid):
        user_list.remove(sid)
        send_notices()
    def on_uexec_event(self,sid,data):
        #
        # 'u_exec_event',{content:vue.$data.sourcecode,loop:true}
        #
        server = get_server()
        if server is None:
            self.emit("error_event",{"message":"没有发现服务器"})
            return 

        print(data)
        data["user_id"] = sid
        if data.get("loop") == True:
            data['loop'] = False
            sio.emit("loop_list_event",data,to=server,namespace="/Kserver")
        else:
            sio.emit("do_exec",data,to=server,namespace="/Kserver")
            
    def on_u_cmd_event(self,sid,data):
        #
        # 'u_cmd_event', {content:"UPDATEALL"}
        #
        if data.get("content") == "UPDATEALL":
            for s in server_list.keys():
                sio.emit("do_updataall",{},s,namespace="/Kserver")
        if data.get("content") == "DOWNLOADALL":
            for s in server_list.keys():
                sio.emit("do_downloadall",{},s,namespace="/Kserver")


sio.register_namespace(Kserver('/Kserver'))
sio.register_namespace(User('/user'))


if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', port)), app)

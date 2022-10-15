# -*- coding: utf-8 -*-
"""
@author: Elaheh Akbari
"""
import socket
import sys
import json


ENCODING = "utf-8"

#stablish a connection with server

def stablish():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    HOST = sys.argv[1]
    PORT = sys.argv[2]  
    s.connect((HOST, int(PORT)))
    return s

conn = stablish()

#handle args and call the right functions based on client order
def main():
    global order
    order = sys.argv[3]
    if order != "subscribe" and order != "publish" and order != "ping":
        print("[PLEASE ENTER ONE CMD: subscribe | publish | ping ]")
        sys.exit()
    else:
        msg = sys.argv[4:]
        if len(msg) < 1 and (order == "subscribe" or order == "publish"):
           print("MORE ARGS NEEDED.")
           sys.exit()
        
    if order == "subscribe":
        subscribe(msg)
        
    elif order == "publish":
        #msg[0] is topic, msg[1] is the message to be published on the topic
        publish(msg[0], msg[1]) 
        
    elif order == "ping":
        ping()
        
    try:
        check()
    except socket.error:
        #handle server timeout
        print("[FAILURE] server timed out.")
    

#send appropriate message to server for subsribing a client
def subscribe(topics):
    conn.send(bytes((json.dumps({"0": order,
                                 "1": topics})), ENCODING))

#send appropriate message to server for publishing a message
def publish(topic, msg):
    conn.send(bytes((json.dumps({"0": order,
                                 "1": topic,
                                 "2": msg})), ENCODING))

#send ping to server
def ping():
    conn.send(bytes((json.dumps({"0" : "ping"})), ENCODING))

#send pong to server as a response for ping
def pong():
    conn.send(bytes((json.dumps({"0" : "pong"})), ENCODING))

#handles received messages from server and prints the result
def check():
    #10s for receiving ack
    conn.settimeout(10.0)
    while True:
        data = conn.recv(1024)
        if not data:
            continue
        
        conn.settimeout(None)
        
        data = data.decode(ENCODING)
        data = json.loads(data)
        
        rcvd = data["0"]
        
        #client subscribed
        if rcvd == "subAck":
            topics = data["1"]
            msg = ""
            for t in topics:
                msg += "[" + t + "]"
            print("[SUCCESS] subscribed. Topics: " + msg)
        
        #error in subscribing
        elif rcvd == "subErr":
            print("[FAILURE] subscription faild!!")
        
        #published message
        elif rcvd == "pubInfo":
            print(data["1"] + " SAID " + data["2"])
            
        elif rcvd == "pubAck":
            print("[SUCCESS] published successfully")
            break
        
        #error in publishing
        elif rcvd == "pubErr":
            print("[FAILURE] publishing failed!!")
        
        elif rcvd == "pong":
            print("[SUCCESS] pong received")
            break
        #error in receiving pong
        elif rcvd == "pongErr":
            print("[FAILURE] error in receiving pong")
        
        #respond to ping with pong
        elif rcvd == "ping":
            pong()
            
        else:
            print("[FAILURE] No valid server response.")

if __name__ == '__main__' :
    main()
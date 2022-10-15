# -*- coding: utf-8 -*-
"""
@author: Elaheh Akbari
"""
import socket
import threading
import json
import time

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 1373  # Port to listen on (non-privileged ports are > 1023)
ENCODING = "utf-8"

#keeps count of client pongs for health check
client_cnt = {}

#keeps subscribers of each topic
topics_subscribers = {}

#keeps count of client pongs
client_addr = {}


#stablishing a connection in main function
def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    s.bind((HOST, PORT))
    
    print("[START] SERVER STARTING...")
    
    s.listen()
    
    #thread to ping every client every 10 secs
    threading.Thread(target = constant_ping).start()
    
    #accept clients
    while True:
        conn, addr = s.accept()
        client_cnt[conn] = 0
        client_addr[conn] = addr
        threading.Thread(target = handler, args = (conn, addr)).start()

#handles clients based on what has been passed as arguments
def handler(conn, addr):
    print('Connected by', addr)
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                continue
            data = data.decode(ENCODING)
            
            #Convert from Python to JSON
            data = json.loads(data)
            
            #"0" is key for order
            #"1" is key for topic
            #"1=2" is key for message
            
            #save client order
            order = data["0"]
            

            #call subscribe function if client asked to subscrie
            #handle failing subscriptions
            if order == "subscribe":
                try:
                    subscribe(data["1"], conn)
                except:
                    #Convert from JSON to Python dict
                    conn.send(bytes((json.dumps({"0" : "subErr"})),ENCODING))
                    
            #call publish function if client asked to publish
            #handle failing publishings        
            if order == "publish":
                try:
                    publish(data["1"], data["2"], conn)
                except:
                    conn.send(bytes((json.dumps({"0" : "pubErr"})),ENCODING))
                    
            #call pong function if client sent a ping
            #handle failing pongs
            if order == "ping":
                try:
                    pong(conn)
                except:
                    conn.send(bytes((json.dumps({"0" : "pongErr"})),ENCODING))
            #pong is received from this client
            #so count for this client can be initialized to zero again                  
            if order == "pong":
                print("[PONG] pong received")
                client_cnt[conn] = 0
                
        #handle disconnecting
        except:
            client_removal(conn)
            print('Disconnected by', addr)
            break


#subscribe to given topics.
def subscribe(topics, conn):
    #add new subscribers
    for topic in topics:
        if topic in topics_subscribers and conn not in topics_subscribers[topic]:
                topics_subscribers[topic].append(conn)
        else:
            topics_subscribers[topic] = [conn]

    #send sub acknowledgement to client
    conn.send(bytes((json.dumps({"0" : "subAck",
                                 "1" : topics})), ENCODING))

#publish message on given topics
def publish(topic, message, conn):
    
    #send publish acknowledgement to client
    conn.send(bytes((json.dumps({"0" : "pubAck"})), ENCODING))

    #publish messages
    for client in topics_subscribers[topic]:
        try:
            client.send(bytes((json.dumps({"0" : "pubInfo",
                                           "1" : topic,
                                           "2" : message})),ENCODING))
        except:
            print("A client not found")
            client_removal(client)


#ping clients
def ping(conn):
    conn.send(bytes((json.dumps({"0" : "ping"})),ENCODING))

#respond to pings from clients
def pong(conn):
    conn.send(bytes((json.dumps( {"0" : "pong"})),ENCODING))

#remove a client after disconnecting
def client_removal(client): 
    if client in topics_subscribers.values():
        topics_subscribers.values().remove(client)
        
    client_cnt.pop(client)
    client_addr.pop(client)
    
    client.close()

#keep pinging all clients every 10s to make sure they are still connected
def constant_ping():
    for client in list(client_cnt):
        #check if client can stay coonnected after each ping
        #based on pongs received
        if client_cnt[client] < 3:
            client_cnt[client] +=  1
            ping(client)
        else:
            client_removal(client)

            
    print("*************** ping clients ***************")
    
    #print connected clients info
    for client in client_addr:
        print("CURRENT CLIENTS: ", client_addr[client])

    time.sleep(10)
    
    constant_ping()
        
if __name__ == '__main__' :
    main()


            



# Message-Broker

This project includes implementing a simple message broker. This intermediary computer program module translates a message from the sender's standard messaging protocol to the receiver's formal messaging protocol. In this project, the TCP protocol is used to transfer commands between [server](/server.py) and [client](/client.py).  

<p align="center">
  <img src="https://user-images.githubusercontent.com/79719208/196032869-0070369b-8b92-437a-b777-981523384a18.png" width=50% height=50%>
</p>

# Commands
## Client to server
* **Publish** sends a message under a specific topic from client to server.
* **Subscribe** informs the server that a client wants to receive a topic-related message.
* **Ping** ensures the connection between the client and server is established.
* **Pong** is a response to the ping sent from the server.
## Server to client
* **Message** sends a message to clients that have subscribed to that topic.
* **SubAck** is sent to acknowledge that the subscription has been successful.
* **PubAck** is sent to acknowledge that publishing has been successful.
* **Ping** ensures the connection between the client and server is established.
* **Pong** is a response to the ping sent from the client.

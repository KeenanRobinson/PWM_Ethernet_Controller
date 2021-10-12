#############################################################
# Description: test program for networking example. Works
# alongside the server_test file.
#
# Created by: Keenan Robinson
# Date: 21/08/2021
# 
# Sources:
# https://www.youtube.com/watch?v=3QiPPX-KeSc&t=2629s
#
#
#############################################################
import socket

HEADER = 64 # Header of 64 bytes to hold the number of bites to be received by the client. Change this accordingly.
PORT = 5050 # arbitrary port that is not being used by something else
FORMAT = 'utf-8' # Define constant to be used for UTF-8 decoding
DISCONNECT_MESSAGE = "!DISCONNECTED"

SERVER_IP = "192.168.0.122" # Determined by the IPv4. 
ADDRESS = (SERVER_IP, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #SOCK_STREAM indicates a TCP socket. For udp, use SOCK_DGRAM
#client.connect(ADDRESS) # Connect the client to the constant tuple with the connection details

def send(message):
    message = message.encode(FORMAT)    # Encode the data to be sent in a byte format
    message_length = len(message)       # Get message length
    send_length = str(message_length).encode(FORMAT) # Message of a certain length, needed to be padded
    send_length += b' ' * (HEADER - len(send_length)) # b here gets the byte representation of the string parameter
    client.send(send_length)
    client.send(message)
    print(client.recv(2048).decode(FORMAT)) #Receive a message of arbitrary size 2048 bytes.

def connect_test():
    client.connect(ADDRESS)
## Client execution
connect_test()
send("Testing!!!")
input() # wait for an input from the console for the client. 
send(DISCONNECT_MESSAGE)


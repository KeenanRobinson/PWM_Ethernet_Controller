#############################################################
# Description: test program for networking example. Works
# alongside the client_test file.
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
import threading


HEADER = 64 # Header of 64 bytes to hold the number of bites to be received by the client. Change this accordingly.
PORT = 5050 # arbitrary port that is not being used by something else
SERVER = socket.gethostbyname(socket.gethostname()) # Local device IPv4 address. Changes as the IP changes
                                                    # .gethostname gets the PC name.
#print(SERVER)
ADDRESS = (SERVER, PORT) #Tuple to bind the IP and the port number
FORMAT = 'utf-8' # Define constant to be used for UTF-8 decoding
DISCONNECT_MESSAGE = "!DISCONNECTED"
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #selects IPv4 to select, and selects it to stream as a TCP connection. Use SOCK_DGRAM for UDP
server.bind(ADDRESS) #binds the tuple to the server object

# Functions
def handle_client(conn, addr): #Handle individual client and server connections. Conn is a socket object.
    # Runs for each client, concurrently for each client
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        message_length = conn.recv(HEADER).decode(FORMAT) #Determines the number of bytes to be received from the client, wiating to receive.

        if message_length: # If the message has some content, we can perform this. Error where there is some blank message
            message = conn.recv(int(message_length)).decode(FORMAT) #Receive the actual message.
            if message == DISCONNECT_MESSAGE: #Cleanly disconnect from the server
                connected = False

            print(f"[{addr}] {message}") #Print out the message from the user.
            conn.send("[SERVER] Message received.".encode(FORMAT)) #Send a message notifying the client that a message was received. 
    
    conn.close()
    print(f"[CLIENT DISCONNECT] [{addr}]")

def handle_client_pwm(conn, addr):
    # Runs for each client, concurrently for each client
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        message_length = conn.recv(HEADER).decode(FORMAT) #Determines the number of bytes to be received from the client, wiating to receive.

        if message_length: # If the message has some content, we can perform this. Error where there is some blank message
            message = conn.recv(int(message_length)).decode(FORMAT) #Receive the main message.
            if message == DISCONNECT_MESSAGE: #Cleanly disconnect from the server
                connected = False
            else:
                print(f"[{addr}] {message}") #Print out the message from the user.
                (pin, duty_cycle) = message_decoder(message)
                print(f"[SERVER] Pin: {pin}")
                print(f"[SERVER] Duty Cycle: {duty_cycle}")
                conn.send("[SERVER] Message received.".encode(FORMAT)) #Send a message notifying the client that a message was received. 
    
    conn.close()
    print(f"[CLIENT DISCONNECT] [{addr}]")
        
def start():
    server.listen() #wait for input, waiting for incoming connections
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True: # Waits for a new connection to the server
        conn, addr = server.accept() # stores the connection information (eg. ports, addresses), conn is a socket object. 
        thread = threading.Thread(target=handle_client_pwm, args=(conn,addr)) # setup a thread that uses a specific handler parsing the connection info as arguments
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount()-1}") # Returns the number of threads, representing the number of client connections. -1 for initial start thread. 

def message_decoder(update_message): # A testing method for the server. See if the data can be extracted
    pin = update_message[0:update_message.find('_')]
    dutyCycle = update_message[update_message.find('_')+1:len(update_message)]
    return pin, dutyCycle


print("[SERVER START-UP] Starting server...")
start()


# Errors encountered:
# Windows I had "Activate.ps1 cannot be loaded because running scripts is disabled on this system."
# fix => Run Powershell as Admin
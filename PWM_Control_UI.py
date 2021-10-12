#############################################################
#                      PWM Controller UI                    #
#############################################################
#region
# Description: main program designed for controlling the
# PWM pins of an Arduino using a Server-Client relationship
# over Ethernet using UDP. 
#
# Created by: Keenan Robinson
# Date modified: 23/08/2021
# 
# Sources:
# https://www.youtube.com/watch?v=3QiPPX-KeSc&t=2629s
#
# Notes:
#   -   Please ensure the config.txt is in the project 
#       directory
#   -   Try not to edit the config.txt file unless you know
#       unless you understand to. Errors may occur otherwise
#   -   A newly updated code is presented in PWM_Control_Ui 
#       using an OOP-based approach which has better 
#       coding practices. 
#   -   Review bugs.txt to review the current known bugs and
#       performance issues.
#
#############################################################
#endregion

import os
from os import read
import socket
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import sys
import time
import threading

# Global constants
DEBUGGING = FALSE #Debugging prints additional information for testing program functionality
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #SOCK_STREAM indicates a TCP socket. For udp, use SOCK_DGRAM
client.settimeout(2) #Sets a 2 second timeout to prevent program hanging if message is not sent.
#For some reason, I am unable to pass the client to the function. Has to be a global variable. *********

class user_interface(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__()
        if DEBUGGING ==  TRUE:
            print(f"[DEBUGGING] args: {args}")
        #Naming the config settings
        ip_address   = args[0][0]
        port         = args[0][1] 
        self.address = (ip_address, port)
        self.theme_saved  = args[0][2] 
        self.height  = args[0][3]
        self.width   = args[0][4]
        self.start_with_no_conn = args[0][6]
        self.initial_conn = args[1]

        ##### Frame setup: #####
        screen_width  = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_pos = int((screen_width/2) - (self.width/2))
        y_pos = int((screen_height/2) - (self.height/2))
        self.geometry(f"{self.width}x{self.height}+{x_pos}+{y_pos}") # width x height + XPOS + YPOS
        self.title("PWM Controller UI")

        style = ttk.Style(self)
        self.load_awthemes()
        style.theme_use(self.theme_saved)
        self.set_background_colour()

        #Request config
        self.pin_configs = self.request_config()

        #Setup ping thread
        self.connection_update_mess = StringVar()
        #Pin labels, tkinter variables to update the labels according to the pins assigned on uC
        self.pin_0_onboard_ref = StringVar()
        self.pin_1_onboard_ref = StringVar()
        self.pin_2_onboard_ref = StringVar()
        self.pin_3_onboard_ref = StringVar() 

        #Duty cycle values to update widgets, note that these are not of type integer yet.
        self.dutyCycle0 = IntVar()
        self.dutyCycle1 = IntVar()
        self.dutyCycle2 = IntVar()
        self.dutyCycle3 = IntVar() 

        #self.ping_thread = threading.Thread(target=self.ping_timer_thread, args=[self.address],daemon=TRUE)
        self.ping_thread = threading.Thread(target=self.ping_timer_thread, daemon=TRUE)
        self.ping_thread.start()

        #Setup widgets
        self.config_widgets()

        ##### Frame setup end #####

    def ping_timer_thread(self):
        print("[CONSOLE] Daemon thread running")
        count = 0
        while True:
            time.sleep(1)
            if count == 5:
                count = 0
                if self.start_with_no_conn:
                    self.connection_update_mess.set("NO CONN-DEBUG")
                    print("[CONSOLE] No ping, but thread is still running.")
                else:
                    client.sendto("!PING".encode(), self.address)
                    # Response:
                    try:
                        rec_message, some_address = client.recvfrom(1024)
                        print(f"[CONSOLE] Received: {rec_message.decode()} (ping_timer_thread)")
                        if rec_message.decode() == 'acknowledged':
                            print("[CONSOLE] Connection status = connected.")
                            if self.connection_update_mess.get() == "NO CONN":
                                #time.sleep(1)
                                self.pin_configs = self.request_config()
                                print(f"[CONSOLE] Pin configurations: {self.pin_configs}")
                                # Reconfigure pins and duty cycles
                                self.pin_0_onboard_ref.set(self.pin_configs[0][0])
                                self.pin_1_onboard_ref.set(self.pin_configs[1][0])
                                self.pin_2_onboard_ref.set(self.pin_configs[2][0])
                                self.pin_3_onboard_ref.set(self.pin_configs[3][0])
                                self.dutyCycle0.set(self.pin_configs[0][1])
                                self.dutyCycle1.set(self.pin_configs[1][1])
                                self.dutyCycle2.set(self.pin_configs[2][1])
                                self.dutyCycle3.set(self.pin_configs[3][1])
                                self.label_reload()
                                self.connection_update_mess.set("CONN")
                                rec_message = "CLEAR MESSAGE"
                        else:
                            print("[CONSOLE] Error, wrong message request [ping_timer_thread]")
                    except socket.timeout:
                        self.connection_update_mess.set("NO CONN")
                        rec_message = ""
                        print("[CONSOLE] Connection status = no connection.")
            else:
                count += 1

    def config_widgets(self):
        generalPadx = 2
        generalPady = 15
        scalePadx = 5
        scalePady = 5
        scaleIPadx = 5
        scaleIPady = 30 #Increase this to increase scale length
        entryWidth = 10  #Increase this increases Entry widget size
        
        print(f"[CONSOLE] Current arduino setup: {self.pin_configs[0]}, {self.pin_configs[1]}, {self.pin_configs[2]}, {self.pin_configs[3]}")
        self.pin_0_onboard_ref.set(self.pin_configs[0][0])
        self.pin_1_onboard_ref.set(self.pin_configs[1][0])
        self.pin_2_onboard_ref.set(self.pin_configs[2][0])
        self.pin_3_onboard_ref.set(self.pin_configs[3][0])

        #Duty cycle values to update widgets, note that these are not of type integer yet.
        self.dutyCycle0.set(self.pin_configs[0][1])
        self.dutyCycle1.set(self.pin_configs[1][1])
        self.dutyCycle2.set(self.pin_configs[2][1])
        self.dutyCycle3.set(self.pin_configs[3][1])

        #Connection message
        self.connection_update_mess = StringVar()
        if self.initial_conn:
            self.connection_update_mess.set("CONN")
        else:
            self.connection_update_mess.set("NO CONN")

        #Create label widgets
        self.pwmLabel0 = ttk.Label(self, text="Pin "+self.pin_0_onboard_ref.get(), font = "Sans 14 bold")
        self.pwmLabel1 = ttk.Label(self, text="Pin "+self.pin_1_onboard_ref.get(), font = "Sans 14 bold")
        self.pwmLabel2 = ttk.Label(self, text="Pin "+self.pin_2_onboard_ref.get(), font = "Sans 14 bold")
        self.pwmLabel3 = ttk.Label(self, text="Pin "+self.pin_3_onboard_ref.get(), font = "Sans 14 bold")
        # Seems to be a ttk.Label error that does not allow the use of textvariable,
        # preventing the text to update according to specific changing text

        #Create entry widgets
        pwmInput0 = ttk.Entry(self, textvariable=self.dutyCycle0, width=entryWidth)
        pwmInput1 = ttk.Entry(self, textvariable=self.dutyCycle1, width=entryWidth)
        pwmInput2 = ttk.Entry(self, textvariable=self.dutyCycle2, width=entryWidth)
        pwmInput3 = ttk.Entry(self, textvariable=self.dutyCycle3, width=entryWidth)
        connection_update = ttk.Entry(self, textvariable=self.connection_update_mess, width=entryWidth, state=DISABLED)

        #Create button widgets
        button0 = ttk.Button(self,text="Set Duty Cycle [0]",command=lambda: self.update_PWM(self.pin_0_onboard_ref.get(),self.dutyCycle0.get()))
        button1 = ttk.Button(self,text="Set Duty Cycle [1]",command=lambda: self.update_PWM(self.pin_1_onboard_ref.get(),self.dutyCycle1.get())) 
        button2 = ttk.Button(self,text="Set Duty Cycle [2]",command=lambda: self.update_PWM(self.pin_2_onboard_ref.get(),self.dutyCycle2.get())) 
        button3 = ttk.Button(self,text="Set Duty Cycle [3]",command=lambda: self.update_PWM(self.pin_3_onboard_ref.get(),self.dutyCycle3.get()))

        #Create scale (sliders)
        pwm0Scale = ttk.Scale(self, from_=100, to=0, variable=self.dutyCycle0, length = self.height*4, orient='vertical',
            command=lambda s:self.dutyCycle0.set('%0.0f' % float(s))) #To remove decimal points, which scales have with ttk
        pwm0Scale.bind("<ButtonRelease-1>", lambda command: self.update_PWM(self.pin_0_onboard_ref.get(), self.dutyCycle0.get()))

        pwm1Scale = ttk.Scale(self, from_=100, to=0, variable=self.dutyCycle1, length = self.height*4, orient='vertical',
            command=lambda s:self.dutyCycle1.set('%0.0f' % float(s))) #To remove decimal points, which scales have with ttk
        pwm1Scale.bind("<ButtonRelease-1>", lambda command: self.update_PWM(self.pin_1_onboard_ref.get(), self.dutyCycle1.get()))

        pwm2Scale = ttk.Scale(self, from_=100, to=0, variable=self.dutyCycle2, length = self.height*4, orient='vertical',
            command=lambda s:self.dutyCycle2.set('%0.0f' % float(s))) #To remove decimal points, which scales have with ttk
        pwm2Scale.bind("<ButtonRelease-1>", lambda command: self.update_PWM(self.pin_2_onboard_ref.get(), self.dutyCycle2.get()))

        pwm3Scale = ttk.Scale(self, from_=100, to=0, variable=self.dutyCycle3, length = self.height*4, orient='vertical',
            command=lambda s:self.dutyCycle3.set('%0.0f' % float(s))) #To remove decimal points, which scales have with ttk
        pwm3Scale.bind("<ButtonRelease-1>", lambda command: self.update_PWM(self.pin_3_onboard_ref.get(), self.dutyCycle3.get()))

        # Ping/test connectivity:
        ping_label = ttk.Label(self, text='Ping Device:', font = "Sans 12 bold")
        ping_button = ttk.Button(self,text="Ping",command=lambda: self.test_connection()) 

        ##Layout configurations:
        #Row and column configurations
        #Rows:
        Grid.rowconfigure(self, 0, weight = 2)
        Grid.rowconfigure(self, 1, weight = 0)
        Grid.rowconfigure(self, 2, weight = 0)
        #Columns:
        for no_of_columns in range(0, 7): # Since there are 7 columns
            if(no_of_columns == 7):
                Grid.columnconfigure(self, no_of_columns, weight = 1)
            else:
                Grid.columnconfigure(self, no_of_columns, weight = 2)

        #Grid geometry handler to layout the GUI
        #Reconfigurable settings for ease of moving components around
        PWM_INPUT_ROWSPAN=6 #Sets the number of rows the scales span over
        #The reason is so that the side panel can be adjusted to include other settings, buttons, etc.
        PWM_LABEL_ROW = PWM_INPUT_ROWSPAN
        PWM_INPUT_ROW = PWM_INPUT_ROWSPAN
        PWM_SCALE_ROW = 0
        BUTTON_ROW    = PWM_INPUT_ROWSPAN+1
        
        #PWM0:
        self.pwmLabel0.grid(row = PWM_LABEL_ROW, column = 0, sticky = W,  pady = generalPady, padx = generalPadx, ipadx=scaleIPadx)
        pwmInput0.grid(row = PWM_INPUT_ROW, column = 1, sticky = W,  pady = generalPady)
        pwm0Scale.grid(row = PWM_SCALE_ROW, column = 0, sticky = '', pady = scalePady, ipady=scaleIPady, columnspan = 2, rowspan=PWM_INPUT_ROWSPAN)
        button0.grid  (row = BUTTON_ROW,    column = 0, sticky = '', pady = generalPady, padx = generalPadx, columnspan = 2)
        #PWM1:
        self.pwmLabel1.grid(row = PWM_LABEL_ROW, column = 2, sticky = W,  pady = generalPady, padx = generalPadx, ipadx=scaleIPadx)
        pwmInput1.grid(row = PWM_INPUT_ROW, column = 3, sticky = W,  pady = generalPady)
        pwm1Scale.grid(row = PWM_SCALE_ROW, column = 2, sticky = '', pady = scalePady, ipady=scaleIPady, columnspan=2, rowspan=PWM_INPUT_ROWSPAN)
        button1.grid  (row = BUTTON_ROW,    column = 2, sticky = '', pady = generalPady, padx = generalPadx, columnspan = 2)
        #PWM2:
        self.pwmLabel2.grid(row = PWM_LABEL_ROW, column = 4, sticky = W,  pady = generalPady, padx = generalPadx, ipadx=scaleIPadx)
        pwmInput2.grid(row = PWM_INPUT_ROW, column = 5, sticky = W,  pady = generalPady)
        pwm2Scale.grid(row = PWM_SCALE_ROW, column = 4, sticky = '', pady = scalePady, ipady=scaleIPady, columnspan=2, rowspan=PWM_INPUT_ROWSPAN)
        button2.grid  (row = BUTTON_ROW,    column = 4, sticky = '', pady = generalPady, padx = generalPadx, columnspan = 2)
        #PWM3:
        self.pwmLabel3.grid(row = PWM_LABEL_ROW, column = 6, sticky = W,  pady = generalPady, padx = generalPadx, ipadx=scaleIPadx)
        pwmInput3.grid(row = PWM_INPUT_ROW, column = 7, sticky = W,  pady = generalPady, ipadx=scaleIPadx)
        pwm3Scale.grid(row = PWM_SCALE_ROW, column = 6, sticky = '', pady = generalPady, ipady=scaleIPady, columnspan=2, rowspan=PWM_INPUT_ROWSPAN)
        button3.grid  (row = BUTTON_ROW,    column = 6, sticky = '', pady = generalPady, padx = generalPadx, columnspan = 2)

        #Ping/connectivity:
        ping_label.grid (row = 3, column = 8, sticky = N, pady = generalPady, padx = generalPadx, ipadx=scaleIPadx)
        ping_button.grid(row = 4, column = 8, sticky = N, pady = generalPady, padx = generalPadx, ipadx=scaleIPadx)
        connection_update.grid(row = 2, column = 8, sticky = N, pady = generalPady, padx = generalPadx, ipadx=scaleIPadx)

    def set_background_colour(self):
        if self.theme_saved == 'awdark':
            self.configure(bg='#33393b')
        elif self.theme_saved == 'awlight':
            self.configure(bg='#e8e8e7')
        elif self.theme_saved == 'classic':
            self.configure(bg='#d9d9d9')
        elif self.theme_saved == 'vista':
            self.configure(bg='#f0f0f0')
        elif self.theme_saved == 'xpnative':
            self.configure(bg='#')
        elif self.theme_saved == 'default':
            self.configure(bg='#d9d9d9')
        elif self.theme_saved == 'winnative':
            self.configure(bg='#f0f0f0')
        elif self.theme_saved == 'clam':
            self.configure(bg='#d9d9d9')
        elif self.theme_saved == 'alt':
            self.configure(bg='#d9d9d9')
        else: 
            pass

    def load_awthemes(self):
        # tell tcl where to find the awthemes packages
        current_directory = os.getcwd()
        current_directory = current_directory.replace("\\", "/")
        current_directory = current_directory[current_directory.find(':')+1:len(current_directory)]
        if DEBUGGING == TRUE:
            print(f"[DEBUGGING] load_awthemes current_directory: {current_directory}")

        self.tk.eval("""
        set dir {/My Projects/PWM_ethernet_controller/awthemes-10.4.0/}

        package ifneeded awthemes 10.4.0 \
            [list source [file join $dir awthemes.tcl]]
        package ifneeded colorutils 4.8 \
            [list source [file join $dir colorutils.tcl]]
        package ifneeded awdark 7.12 \
            [list source [file join $dir awdark.tcl]]
        package ifneeded awlight 7.10 \
            [list source [file join $dir awlight.tcl]]
        """)
        # load the awdark and awlight themes
        self.tk.call("package", "require", 'awdark')
        self.tk.call("package", "require", 'awlight')
        #print(style.theme_names())

    def request_config(self):
        #Using the port and address supplied in the config.txt, send device a specific packet
        #and check for a proper response. 
        global client
        req_message = "!REQUEST_CONFIG" # Main message sent to arduino
        if self.start_with_no_conn:
            return [["0"    , 0],
                    ["1"    , 0],
                    ["2"    , 0],
                    ["3"    , 0]]
        else:
            print(f"[CONSOLE] Requesting config from device on {self.address}")
            client.sendto(req_message.encode(), self.address)
            # Response:
            try:
                receive_message, address = client.recvfrom(1024)
                print(receive_message.decode())
                receive_message = receive_message.decode()
                if receive_message.find('_') != -1:
                    print('[CONSOLE] Message request successful. Server/host correctly responded.')
                    config_elements = string_splicer(receive_message, "|") # Separates the string to extract each individual pin config
                    pin_0_config = config_elements[0]
                    pin_1_config = config_elements[1]
                    pin_2_config = config_elements[2]
                    pin_3_config = config_elements[3]
                    #print(f"{pin_0_config}")
                    #print(string_splicer(pin_0_config, "_"))
                    [pin_0_onboard_ref, pin_0_dutycycle] = string_splicer(pin_0_config, "_")
                    [pin_1_onboard_ref, pin_1_dutycycle] = string_splicer(pin_1_config, "_")
                    [pin_2_onboard_ref, pin_2_dutycycle] = string_splicer(pin_2_config, "_")
                    [pin_3_onboard_ref, pin_3_dutycycle] = string_splicer(pin_3_config, "_")
                    receive_message = ""
                    return [[pin_0_onboard_ref  , int(pin_0_dutycycle)], 
                            [pin_1_onboard_ref  , int(pin_1_dutycycle)],
                            [pin_2_onboard_ref  , int(pin_2_dutycycle)],
                            [pin_3_onboard_ref  , int(pin_3_dutycycle)],
                            [TRUE               , 1]]
                else:
                    print('[CONSOLE] Error: Incorrect server response (request_config)')
                    return [["0"    , 0],
                            ["1"    , 0],
                            ["2"    , 0],
                            ["3"    , 0]]
            except socket.timeout:
                print('[CONSOLE] Error: No response received from server/host device. Please check the connection.')
                return [["0"    , 0],
                        ["1"    , 0],
                        ["2"    , 0],
                        ["3"    , 0]]

    def update_PWM(self, pwm_pin, duty_cycle):
        global client
        if self.check_valid_duty_cycle(duty_cycle) == 1:
            print(f"[CONSOLE] Pin: {pwm_pin}, Duty cycle: {duty_cycle}")
            pwm_message = f"{pwm_pin}_{duty_cycle}" # Main message containing PWM update data
            if self.start_with_no_conn:
                print("[CONSOLE] No update performed. (start_with_no_conn=1)")
            else:
                client.sendto(pwm_message.encode(), self.address)
        else:
            print("[CONSOLE] Internal error. Duty cycle is of an incorrect type.")

    def check_valid_duty_cycle(self, input_value):
        #Simple error checking function to ensure that a valid duty cycle is sent
        if isinstance(input_value, int) & ((input_value <= 100) & (input_value >= 0)):
            return 1
        else:
            return 0

    def test_connection(self):
         #Using the port and address supplied in the config.txt, send device a specific packet
        #and check for a proper response. 
        print(f"[CONSOLE] Pinging device on {self.address}")
        ping_message = "!PING_test" # Main message sent to arduino
        client.sendto(ping_message.encode(), self.address)
        # Response:
        try:
            receive_message, address = client.recvfrom(1024)
            print(f"[CONSOLE] Message received from host: {receive_message.decode()} (test_connection())")
            if receive_message.decode() == 'acknowledged_test':
                print('[CONSOLE] Connection successful. Ping was received and server/host correctly responded. (test_connection)')
                receive_message = "CLEAR MESSAGE"
                return 1
        except socket.timeout:
            print('[CONSOLE] Error: No response received from server/host device. Please check the connection. (test_connection)')
            return 0
    
    def label_reload(self):
        self.pwmLabel0.configure(text="Pin "+self.pin_0_onboard_ref.get())
        self.pwmLabel1.configure(text="Pin "+self.pin_1_onboard_ref.get())
        self.pwmLabel2.configure(text="Pin "+self.pin_2_onboard_ref.get())
        self.pwmLabel3.configure(text="Pin "+self.pin_3_onboard_ref.get())
        
def read_config():
    FILENAME = "config.txt"
    lines=[]
    try:
        with open(FILENAME, "r") as f:
            lines=f.read().splitlines()
            #print(lines)
            for i in range(len(lines)):
                # IP address settings:
                if lines[i].find("//") >= 0:
                    pass
                elif lines[i].find("ip") != -1: #If the ip config is found
                    ip_address = lines[i][lines[i].find('=')+1:len(lines[i])] #Extract setting data
                    ip_address = str(ip_address)
                    if DEBUGGING == TRUE:
                        print(f"[DEBUGGING]: ip = {ip_address}")
                # Port settings:
                elif lines[i].find("port") != -1: #If the ip config is found
                    port = lines[i][lines[i].find('=')+1:len(lines[i])] #Extract setting data
                    port = int(port)
                    if DEBUGGING == TRUE:
                        print(f"[DEBUGGING]: port = {port}")
                #Theme settings
                elif lines[i].find("theme") != -1: #If the theme config is found
                    theme_saved = lines[i][lines[i].find('=')+1:len(lines[i])] #Extract setting data
                    if DEBUGGING == TRUE:
                        print(f"[DEBUGGING]: theme = {theme_saved}")
                # height settings
                elif lines[i].find("height") != -1: #If the config is found
                    height = lines[i][lines[i].find('=')+1:len(lines[i])] #Extract setting data
                    height = int(height)
                    if DEBUGGING == TRUE:
                        print(f"[DEBUGGING]: height = {height}")
                # width settings
                elif lines[i].find("width") != -1: #If the config is found
                    width = lines[i][lines[i].find('=')+1:len(lines[i])] #Extract setting data
                    width = int(width)
                    if DEBUGGING == TRUE:
                        print(f"[DEBUGGING]: width = {width}")
                # no_start_on_no_conn settings
                elif lines[i].find("no_start_on_no_conn") != -1: #If the config is found
                    no_start_on_no_conn = lines[i][lines[i].find('=')+1:len(lines[i])] #Extract setting data
                    no_start_on_no_conn = int(no_start_on_no_conn)
                    if DEBUGGING == TRUE:
                        print(f"[DEBUGGING]: no_start_on_no_conn = {no_start_on_no_conn}")
                elif lines[i].find("no_start_on_no_conn") != -1: #If the config is found
                    no_start_on_no_conn = lines[i][lines[i].find('=')+1:len(lines[i])] #Extract setting data
                    no_start_on_no_conn = int(no_start_on_no_conn)
                    if DEBUGGING == TRUE:
                        print(f"[DEBUGGING]: no_start_on_no_conn = {no_start_on_no_conn}")
                # start_with_no_conn settings
                elif lines[i].find("start_with_no_conn") != -1: #If the config is found
                    start_with_no_conn = lines[i][lines[i].find('=')+1:len(lines[i])] #Extract setting data
                    start_with_no_conn = int(start_with_no_conn)
                    if DEBUGGING == TRUE:
                        print(f"[DEBUGGING]: start_with_no_conn = {start_with_no_conn}")
        f.close()
        return [ip_address, port, theme_saved, height, width, no_start_on_no_conn, start_with_no_conn]
    except Exception as e:
        print("Error:"+str(e))
        sys.exit(1)

def test_connection(address):
    #Using the port and address supplied in the config.txt, send device a specific packet
    #and check for a proper response. 
    print(f"[CONSOLE] Pinging device on {address}")
    ping_message = "!PING" # Main message sent to arduino
    client.sendto(ping_message.encode(), address)
    # Response:
    try:
        receive_message, address = client.recvfrom(1024)
        print(f"Message received from host: {receive_message.decode()}")
        if receive_message.decode() == 'acknowledged':
            print('[CONSOLE] Connection successful. Ping was received and server/host correctly responded.')
            return 1
    except socket.timeout:
        print('[CONSOLE] Error: No response received from server/host device. Please check the connection.')
        return 0

def string_splicer(search_string, index_char):
    #A function that separates a string into lists based on index of a known character
    # eg. "|test|test1|test2|" => ['test', 'test2', 'test3']

    return_list = []
    first_index = 0
    while search_string.find(index_char) != -1:
        #First occurence:
        first_index = search_string.find(index_char)
        single_value = search_string[0: first_index]
        return_list.append(single_value)
        search_string = search_string[first_index+1: len(search_string)]
    
    return_list.append(search_string)    
    return return_list

def main():
    #Start reading config.txt, for start up settings
    config_settings = read_config()
    if DEBUGGING == TRUE:
        print("[DEBUGGING] DEBUGGING ENABLED")
        print(config_settings)
    ip_address  = config_settings[0]
    port        = config_settings[1] 
    address = (ip_address, port)
    no_start_on_no_conn = config_settings[5]
    start_with_no_conn  = config_settings[6]

    conn_result = 0 # Initial start-up connection result
    if no_start_on_no_conn & (start_with_no_conn == 0):
            conn_result = test_connection(address)
            if conn_result == 0:
                #Connection failed
                messagebox.showerror("Connection Error", "Error: No response received from server/host device. Please check the connection.")
                #messagebox.showinfo("Details", "Error: No response received from server/host device. Please check the connection.")
                sys.exit(1)
            else: 
                conn_result = 1

    app = user_interface(config_settings, conn_result)
    app.mainloop()

if __name__ == '__main__':
    main()
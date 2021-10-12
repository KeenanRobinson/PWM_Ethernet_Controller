#############################################################
#               ControlApplication_test.py                  #
#############################################################
#region
# Description: main program designed for controlling the
# PWM pins of an Arduino using a Server-Client relationship
# over Ethernet. 
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
from tkinter import *
from tkinter import ttk
import sys
import time
import threading

# Constants
HEADER = 64         # Header of 64 bytes to hold the number of bites to be received by the client. Change this accordingly.
FORMAT = 'utf-8'    # Define constant to be used for UTF-8 decoding
DEBUGGING = FALSE  #To be removed, was just for testing. Just meant to disable networking
HEIGHT=480
WIDTH=960

#Global variables
ip_address = 0
address = 0
port = 0
debugging = FALSE  #To be removed, was just for testing. Just meant to disable networking


# Networking
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #SOCK_STREAM indicates a TCP socket. For udp, use SOCK_DGRAM
client.settimeout(2) #Sets a 2 second timeout to prevent program hanging if message is not sent. 

# Tkinter setup
root = Tk() # Create root window object
root.title("Arduino PWM Controller")
#Centering the application relative to screen:
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_pos = int((screen_width/2) - (WIDTH/2))
y_pos = int((screen_height/2) - (HEIGHT/2))
root.geometry(f"{WIDTH}x{HEIGHT}+{x_pos}+{y_pos}") # width x height + XPOS + YPOS
style = ttk.Style(root) # Create an instance of ttk Style class
FILENAME="config.txt" # To store configuration data for when the program is restarted
connection_update_mess = StringVar()

def main_window_setup(): # Sets up the main window configuration
    generalPadx = 2
    generalPady = 15
    scalePadx = 5
    scalePady = 5
    scaleIPadx = 5
    scaleIPady = 30 #Increase this to increase scale length
    entryWidth = 10  #Increase this increases Entry widget size


    ping_thread = threading.Thread(target=ping_timer_thread, daemon=TRUE)
    ping_thread.start()

    #Pin labels, tkinter variables to update the labels according to the pins assigned on uC
    pin_0_onboard_ref = StringVar()
    pin_1_onboard_ref = StringVar()
    pin_2_onboard_ref = StringVar()
    pin_3_onboard_ref = StringVar() 
    configs = request_config() # Initial configs
    pin_configs = [configs[0], configs[1], configs[2], configs[3]] #Holds the pin numbers setup on Arduino and current duty cycles
    
    print(f"[CONSOLE] Current arduino setup: {pin_configs[0]}, {pin_configs[1]}, {pin_configs[2]}, {pin_configs[3]}")
    pin_0_onboard_ref.set(pin_configs[0][0])
    pin_1_onboard_ref.set(pin_configs[1][0])
    pin_2_onboard_ref.set(pin_configs[2][0])
    pin_3_onboard_ref.set(pin_configs[3][0])

    #Duty cycle values to update widgets, note that these are not of type integer yet.
    dutyCycle0 = IntVar()
    dutyCycle1 = IntVar()
    dutyCycle2 = IntVar()
    dutyCycle3 = IntVar() 
    dutyCycle0.set(pin_configs[0][1])
    dutyCycle1.set(pin_configs[1][1])
    dutyCycle2.set(pin_configs[2][1])
    dutyCycle3.set(pin_configs[3][1])

    #Theme setting value to be changed for the application asthaetic
    app_theme = StringVar()

    #Create label widgets
    pwmLabel0 = ttk.Label(root, text="Pin "+pin_0_onboard_ref.get(), font = "Sans 14 bold")
    pwmLabel1 = ttk.Label(root, text="Pin "+pin_1_onboard_ref.get(), font = "Sans 14 bold")
    pwmLabel2 = ttk.Label(root, text="Pin "+pin_2_onboard_ref.get(), font = "Sans 14 bold")
    pwmLabel3 = ttk.Label(root, text="Pin "+pin_3_onboard_ref.get(), font = "Sans 14 bold")
    # Seems to be a ttk.Label error that does not allow the use of textvariable,
    # preventing the text to update according to specific changing text

    #Create entry widgets
    pwmInput0 = ttk.Entry(root, textvariable=dutyCycle0, width=entryWidth)
    pwmInput1 = ttk.Entry(root, textvariable=dutyCycle1, width=entryWidth)
    pwmInput2 = ttk.Entry(root, textvariable=dutyCycle2, width=entryWidth)
    pwmInput3 = ttk.Entry(root, textvariable=dutyCycle3, width=entryWidth)
    connection_update = ttk.Entry(root, textvariable=connection_update_mess, width=entryWidth, state=DISABLED)

    #Create button widgets
    button0 = ttk.Button(root,text="Set Duty Cycle [0]",command=lambda: update_PWM(pin_0_onboard_ref.get(),dutyCycle0.get()))
    button1 = ttk.Button(root,text="Set Duty Cycle [1]",command=lambda: update_PWM(pin_1_onboard_ref.get(),dutyCycle1.get())) 
    button2 = ttk.Button(root,text="Set Duty Cycle [2]",command=lambda: update_PWM(pin_2_onboard_ref.get(),dutyCycle2.get())) 
    button3 = ttk.Button(root,text="Set Duty Cycle [3]",command=lambda: update_PWM(pin_3_onboard_ref.get(),dutyCycle3.get()))

    #Create scale (sliders)
    pwm0Scale = ttk.Scale(root, from_=100, to=0, variable=dutyCycle0, length = HEIGHT*4, orient='vertical',
        command=lambda s:dutyCycle0.set('%0.0f' % float(s))) #To remove decimal points, which scales have with ttk
    pwm0Scale.bind("<ButtonRelease-1>", lambda command: update_PWM(pin_0_onboard_ref.get(), dutyCycle0.get()))

    pwm1Scale = ttk.Scale(root, from_=100, to=0, variable=dutyCycle1, length = HEIGHT*4, orient='vertical',
        command=lambda s:dutyCycle1.set('%0.0f' % float(s))) #To remove decimal points, which scales have with ttk
    pwm1Scale.bind("<ButtonRelease-1>", lambda command: update_PWM(pin_1_onboard_ref.get(), dutyCycle1.get()))

    pwm2Scale = ttk.Scale(root, from_=100, to=0, variable=dutyCycle2, length = HEIGHT*4, orient='vertical',
        command=lambda s:dutyCycle2.set('%0.0f' % float(s))) #To remove decimal points, which scales have with ttk
    pwm2Scale.bind("<ButtonRelease-1>", lambda command: update_PWM(pin_2_onboard_ref.get(), dutyCycle2.get()))

    pwm3Scale = ttk.Scale(root, from_=100, to=0, variable=dutyCycle3, length = HEIGHT*4, orient='vertical',
        command=lambda s:dutyCycle3.set('%0.0f' % float(s))) #To remove decimal points, which scales have with ttk
    pwm3Scale.bind("<ButtonRelease-1>", lambda command: update_PWM(pin_3_onboard_ref.get(), dutyCycle3.get()))

    # Theme combobox, using ttk
    theme_label = ttk.Label(root, text='Theme select:', font = "Sans 12 bold")
    theme_combobox = ttk.Combobox(root, textvariable=app_theme, font = "Sans 12")
    theme_combobox.bind('<<ComboboxSelected>>', lambda command: change_theme(app_theme.get()))
    theme_combobox['values'] = style.theme_names() #Store the themes as a list

    # Ping/test connectivity:
    ping_label = ttk.Label(root, text='Ping Device:', font = "Sans 12 bold")
    ping_button = ttk.Button(root,text="Ping",command=lambda: test_connection()) 
    #ping_button = ttk.Button(root,text="Ping",command=lambda: test_connection()) 

    ##Layout configurations:
    #Row and column configurations
    #Rows:
    Grid.rowconfigure(root, 0, weight = 2)
    Grid.rowconfigure(root, 1, weight = 0)
    Grid.rowconfigure(root, 2, weight = 0)
    #Columns:
    for no_of_columns in range(0, 7): # Since there are 7 columns
        if(no_of_columns == 7):
            Grid.columnconfigure(root, no_of_columns, weight = 1)
        else:
            Grid.columnconfigure(root, no_of_columns, weight = 2)

    #Grid geometry handler to layout the GUI
    #Reconfigurable settings for ease of moving components around
    PWM_INPUT_ROWSPAN=6 #Sets the number of rows the scales span over
    #The reason is so that the side panel can be adjusted to include other settings, buttons, etc.
    PWM_LABEL_ROW = PWM_INPUT_ROWSPAN
    PWM_INPUT_ROW = PWM_INPUT_ROWSPAN
    PWM_SCALE_ROW = 0
    BUTTON_ROW    = PWM_INPUT_ROWSPAN+1

    #PWM0:
    pwmLabel0.grid(row = PWM_LABEL_ROW, column = 0, sticky = W,  pady = generalPady, padx = generalPadx, ipadx=scaleIPadx)
    pwmInput0.grid(row = PWM_INPUT_ROW, column = 1, sticky = W,  pady = generalPady)
    pwm0Scale.grid(row = PWM_SCALE_ROW, column = 0, sticky = '', pady = scalePady, ipady=scaleIPady, columnspan = 2, rowspan=PWM_INPUT_ROWSPAN)
    button0.grid  (row = BUTTON_ROW, column = 0, sticky = '', pady = generalPady, padx = generalPadx, columnspan = 2)
    #PWM1:
    pwmLabel1.grid(row = PWM_LABEL_ROW, column = 2, sticky = W,  pady = generalPady, padx = generalPadx, ipadx=scaleIPadx)
    pwmInput1.grid(row = PWM_INPUT_ROW, column = 3, sticky = W,  pady = generalPady)
    pwm1Scale.grid(row = PWM_SCALE_ROW, column = 2, sticky = '', pady = scalePady, ipady=scaleIPady, columnspan=2, rowspan=PWM_INPUT_ROWSPAN)
    button1.grid  (row = BUTTON_ROW, column = 2, sticky = '', pady = generalPady, padx = generalPadx, columnspan = 2)
    #PWM2:
    pwmLabel2.grid(row = PWM_LABEL_ROW, column = 4, sticky = W,  pady = generalPady, padx = generalPadx, ipadx=scaleIPadx)
    pwmInput2.grid(row = PWM_INPUT_ROW, column = 5, sticky = W,  pady = generalPady)
    pwm2Scale.grid(row = PWM_SCALE_ROW, column = 4, sticky = '', pady = scalePady, ipady=scaleIPady, columnspan=2, rowspan=PWM_INPUT_ROWSPAN)
    button2.grid  (row = BUTTON_ROW, column = 4, sticky = '', pady = generalPady, padx = generalPadx, columnspan = 2)
    #PWM3:
    pwmLabel3.grid(row = PWM_LABEL_ROW, column = 6, sticky = W,  pady = generalPady, padx = generalPadx, ipadx=scaleIPadx)
    pwmInput3.grid(row = PWM_INPUT_ROW, column = 7, sticky = W,  pady = generalPady, ipadx=scaleIPadx)
    pwm3Scale.grid(row = PWM_SCALE_ROW, column = 6, sticky = '', pady = generalPady, ipady=scaleIPady, columnspan=2, rowspan=PWM_INPUT_ROWSPAN)
    button3.grid  (row = BUTTON_ROW, column = 6, sticky = '', pady = generalPady, padx = generalPadx, columnspan = 2)

    #Theme combobox:
    theme_label.grid(row = 5, column = 8, sticky = N, pady = generalPady, padx = generalPadx, ipadx=scaleIPadx)
    theme_combobox.grid(row = 6, column = 8, sticky = N, pady = generalPady, padx = 10, ipadx=10)

    #Ping/connectivity:
    ping_label.grid (row = 3, column = 8, sticky = N, pady = generalPady, padx = generalPadx, ipadx=scaleIPadx)
    ping_button.grid(row = 4, column = 8, sticky = N, pady = generalPady, padx = generalPadx, ipadx=scaleIPadx)
    connection_update.grid(row = 2, column = 8, sticky = N, pady = generalPady, padx = generalPadx, ipadx=scaleIPadx)
    # Notes for this section: ipady= effectively adjusts the slider size. Increase this 
    # if you need to be more accurate.

# Application functions
def read_config():
    global ip_address
    global port
    lines=[]
    try:
        with open(FILENAME, "r") as f:
            lines=f.read().splitlines()
            #print(lines)
            for i in range(len(lines)):
                #PWM pin select configuration:
                #if lines[i].find('pwmPin') != -1: #if the config setting is a pwmPin configuration
                #    pinNumber = lines[i][lines[i].find('=')+1:len(lines[i])] #Extract setting data
                #    pins.append(int(pinNumber)) # Append the pin to the pin list
                if lines[i].find("ip") != -1: #If the ip config is found
                    ip_address = lines[i][lines[i].find('=')+1:len(lines[i])] #Extract setting data
                    ip_address = str(ip_address)
                elif lines[i].find("port") != -1: #If the ip config is found
                    port = lines[i][lines[i].find('=')+1:len(lines[i])] #Extract setting data
                    port = int(port)
                elif lines[i].find("theme") != -1: #If the theme config is found
                    theme_saved = lines[i][lines[i].find('=')+1:len(lines[i])] #Extract setting data
                    try:
                        #print(theme_saved)
                        style.theme_use(theme_saved)
                        set_background_colour(theme_saved)
                    except:
                        print("[CONSOLE] Error: problem loading theme, defaulting to vista")
                        editted_setting = edit_file("config.txt", "theme=", 'vista')
                        set_background_colour('vista')
        f.close()
        return [ip_address, port, theme_saved]
    except Exception as e:
        print("Error:"+str(e))
        sys.exit(1)

def update_config(option, value):
    #lines=[]
    #if option == 'theme=':
    #    with open(filename, "w") as f:
    #        lines=f.read().splitlines()
    #        for i in range(len(lines)):
    #            if lines[i].find(option) != -1:
    #                setting_to_change = lines[i][lines[i].find('=')+1:len(lines[i])] #Extract setting data
    #                lines[i].replace(setting_to_change, value)
    #            
    #        
    #    f.close()
    pass

def edit_file(filename, setting_key, setting_value):
    #Setting key explicit format: SETTING_NAME=
    lines = []
    new_lines = []
    setting_edited=False
    with open(filename, 'r') as f:
	    lines = f.readlines() #Store lines in a list
	    #Find the line to edit 
    f.close()
    for i in range(len(lines)):
        if lines[i].find(setting_key) != -1: #Setting found
            new_line = lines[i][0:lines[i].find('=')+1] + setting_value #append the new setting
            new_lines.append(new_line)
            setting_edited = True
        else:
            new_lines.append(lines[i])

    if setting_edited == True:
        with open(filename, 'w') as f:
	    #for i in range(0, len(new_lines))
	    #    f.write(new_lines[i]+'\n')
	        f.writelines(new_lines)
    else:
	    pass
    return setting_edited

def change_theme(theme_name): # Function to change the current application theme
    #Dark themes:
    dark_themes = ['awdark']
    #Change the theme
    style.theme_use(theme_name)
    editted_setting = edit_file("config.txt", "theme=", theme_name)
    if editted_setting: 
        print("[CONSOLE]: Config setting was successfully changed.")
        set_background_colour(theme_name)
    else:
        print("[CONSOLE]: Config setting change was unsuccessful.")

def main():
    print("Welcome to the PWM Controller application. Please ensure the device is setup, powered and connected.")
    print("Please note: adjust the IP address of the device to connect to in the config.txt")
    load_awthemes() #Load the custom and native ttk themes for the application
    client_connection_handler() #Begins IP and port assignment
    main_window_setup()
    root.mainloop() # Starts tkinter application in an event listening loop, opens main_window

def cleanup():
    pass

def load_awthemes():
    # tell tcl where to find the awthemes packages
    current_directory = os.getcwd()
    current_directory = current_directory.replace("\\", "/")
    current_directory = current_directory[current_directory.find(':')+1:len(current_directory)]
    print(current_directory)

    root.tk.eval("""
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
    root.tk.call("package", "require", 'awdark')
    root.tk.call("package", "require", 'awlight')
    #print(style.theme_names())

def set_background_colour(theme_name):
    if theme_name == 'awdark':
        root.configure(bg='#33393b')
    elif theme_name == 'awlight':
        root.configure(bg='#e8e8e7')
    elif theme_name == 'classic':
        root.configure(bg='#d9d9d9')
    elif theme_name == 'vista':
        root.configure(bg='#f0f0f0')
    elif theme_name == 'xpnative':
        root.configure(bg='#f0f0f0')
    elif theme_name == 'default':
        root.configure(bg='#d9d9d9')
    elif theme_name == 'winnative':
        root.configure(bg='#f0f0f0')
    elif theme_name == 'clam':
        root.configure(bg='#d9d9d9')
    elif theme_name == 'alt':
        root.configure(bg='#d9d9d9')
    else: 
        pass
        
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

def check_valid_value(input_value):
    #Simple error checking function to ensure that a valid duty cycle is sent
    if isinstance(input_value, int) & ((input_value <= 100) & (input_value >= 0)):
        return 1
    else:
        return 0
# Network functions
def client_connection_handler():
    global address
    read_config()    
    print(f"[CONSOLE] Transmitting on IP: {ip_address}")
    print(f"[CONSOLE] Transmitting on port: {port}")
    address=(ip_address, port) 

def update_PWM(pwm_pin, duty_cycle):
    if check_valid_value(duty_cycle) == 1:
        print(f"[CONSOLE] Pin: {pwm_pin}, Duty cycle: {duty_cycle}")
        pwm_message = f"{pwm_pin}_{duty_cycle}" # Main message containing PWM update data
        #pwm_message = pwm_message.encode(FORMAT) # Encode main message
        #message_len = len(pwm_message) # Create initial header message detailing main message length
        #message_len = str(message_len).encode(FORMAT) # Encode the header message to be padded
        #message_len += b' ' * (HEADER - len(message_len)) # b here gets the byte representation of the string parameter,
        if DEBUGGING == False:
            client.sendto(pwm_message.encode(), address)
    else:
        print("[CONSOLE] Internal error. Duty cycle is of an incorrect type.")

def test_connection():
    #Using the port and address supplied in the config.txt, send device a specific packet
    #and check for a proper response. 
    global address

    print(f"[CONSOLE] Pinging device on {address}")
    ping_message = "!PING" # Main message sent to arduino
    if DEBUGGING == False:
        client.sendto(ping_message.encode(), address)
        # Response:
        try:
            receive_message, address = client.recvfrom(1024)
            print(receive_message.decode())
            if receive_message.decode() == 'acknowledged':
                print('[CONSOLE] Connection successful. Ping was received and server/host correctly responded.')
        except socket.timeout:
            print('[CONSOLE] Error: No response received from server/host device. Please check the connection.')

def request_config():
    #Using the port and address supplied in the config.txt, send device a specific packet
    #and check for a proper response. 
    global address
    print(f"[CONSOLE] Requesting config from device on {address}")
    req_message = "!REQUEST_CONFIG" # Main message sent to arduino
    if DEBUGGING == False:
        client.sendto(req_message.encode(), address)
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

                return [[pin_0_onboard_ref  , int(pin_0_dutycycle)], 
                        [pin_1_onboard_ref  , int(pin_1_dutycycle)],
                        [pin_2_onboard_ref  , int(pin_2_dutycycle)],
                        [pin_3_onboard_ref  , int(pin_3_dutycycle)],
                        [TRUE               , 1]]
        except socket.timeout:
            print('[CONSOLE] Error: No response received from server/host device. Please check the connection.')
            return [["0"    , 0],
                    ["1"    , 0],
                    ["2"    , 0],
                    ["3"    , 0],
                    [FALSE  , 0]]

def ping_timer_thread():
    global address
    print("Daemon thread running")
    count = 0
    while True:
        time.sleep(1)
        if count == 5:
            count = 0
            client.sendto("!PING".encode(), address)
            # Response:
            try:
                receive_message, address = client.recvfrom(1024)
                print(receive_message.decode())
                if receive_message.decode() == 'acknowledged':
                    connection_update_mess.set("CONN")
                    print("[CONSOLE] Connection status = connected.")
            except socket.timeout:
                connection_update_mess.set("NO CONN")
                print("[CONSOLE] Connection status = no connection.")
        else:
            count += 1

if __name__ == '__main__':
    main()
    cleanup()

#Notes:
# - client.send() is used for TCP sockets, client.sendto() is used for UDP
# - client.recv() is used for TCP sockets, client.recvfrom() is used for UDP


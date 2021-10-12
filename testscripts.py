#Basic environment for testing functions

#def string_splicer(search_string, index_char):
    #A function that separates a string into lists based on index of a known character
    # eg. "|test|test1|test2|" => ['test', 'test2', 'test3']

 #   return_list = []
#    first_index = 0
#    while search_string.find(index_char) != -1:
#        #First occurence:
#        first_index = search_string.find(index_char)
#        single_value = search_string[0: first_index]
#        return_list.append(single_value)
#        search_string = search_string[first_index+1: len(search_string)]
#    
#    return_list.append(search_string[first_index: len(search_string)])    
#    return return_list

#def check_valid_value(input_value):
#    #Simple error checking function to ensure that a valid duty cycle is sent
#    if isinstance(input_value, int) & ((input_value <= 100) & (input_value >= 0)):
#        return 1
#    else:
#        return 0

#if __name__ == '__main__':
    #test_string = "|test|test1|test2|"
    #values = string_splicer(test_string, '|')
    #print(f"{values}")

    #Check check_valid_value(input_value):
#    test_value = 100.0
#    print(check_valid_value(test_value))


import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo, showerror


class TemperatureConverter:
    @staticmethod
    def fahrenheit_to_celsius(f):
        return (f - 32) * 5/9


class MainFrame:
    def __init__(self, master):
        myFrame = tk.Frame(master)
        myFrame.pack()

        self.myButton = ttk.Button(master, text="Click me!", command=self.clicker)
        self.myButton.pack(pady=20)
    
    def clicker(self):
        print("CLICKER")


if __name__ == "__main__":
    root = tk.Tk()
    app = MainFrame(root)
    root.mainloop()

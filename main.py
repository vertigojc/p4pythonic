import tkinter as tk

def add_input():
    # create a new text input widget
    new_input = tk.Entry(window)
    
    # pack the new input widget onto the window
    new_input.pack()
    
    # create a new button widget
    new_button = tk.Button(window, text="Delete", command=lambda: delete_input(new_input, new_button))
    
    # pack the new button widget onto the window
    new_button.pack()
    
def delete_input(input_widget, button_widget):
    # destroy the input widget and button widget
    input_widget.destroy()
    button_widget.destroy()

# create a new tkinter window
window = tk.Tk()

# set the window title
window.title("Dynamic Inputs")

# create a button widget to add new inputs
add_button = tk.Button(window, text="Add", command=add_input)

# pack the add button onto the window
add_button.pack()



# start the tkinter event loop
window.mainloop()

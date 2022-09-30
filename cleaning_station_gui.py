from positioning_screen import *
from actuator_screen import *


#=====================================#
def show_actuator():
    pos_frame.pack_forget()
    home_frame.pack_forget()
    # board.flush()
    board.write(b'P')
    show_act_screen()


def show_pos_screen():
    frame.pack_forget()
    act_frame.pack_forget()
    home_frame.pack_forget()
    # board.flush()
    board.write(b'A')
    pos_frame.pack()


def home_screen():
    frame.pack_forget()
    act_frame.pack_forget()
    pos_frame.pack_forget()
    # board.flush()
    board.write(b'C')
    home_frame.pack()


#======================================#
home_frame = Frame(root)

start_up_label = Label(home_frame, text='Select a Mode')
pos_home_button.configure(command=home_screen)
home_button.configure(command=home_screen)
act_screen_button = Button(
    home_frame, text='Actuator and Pump Operation', command=show_actuator)
pos_screen_button = Button(
    home_frame, text='Actuator Positioning', command=show_pos_screen)

start_up_label.grid(row=0, column=0)
act_screen_button.grid(row=1, column=0)
pos_screen_button.grid(row=2, column=0)

# board.close()
# board = serial.Serial('COM3', 9600, timeout=1)
# board.flush()
# time.sleep(0.5)
home_screen()
root.mainloop()

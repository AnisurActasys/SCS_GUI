from tkinter import *
from StepperMotorsV4 import *
import serial


root = Tk()
writedic = {}
pos_frame = Frame(root)


def submit():
    writedic['X'] = str(x_var.get())
    writedic['Y'] = str(y_var.get())
    writedic['Actuator Mount'] = str(theta_var.get())
    writedic['Reset'] = str(reset_var.get())
    writedic['Distance X'] = x_distance_entry.get()
    writedic['Distance Y'] = y_distance_entry.get()
    writedic['Angle'] = theta_angle_entry.get()
    executeIns()


def holder_func():
    print('presed')
    pass
# def sel1():
#     writedic['X'] = str(x_var.get())


# def sel2():
#     writedic['Y'] = str(y_var.get())


# def sel3():
#     writedic['Actuator Mount'] = str(var2.get())

# def sel4():
#     writedic['Reset'] = str(var3.get())

#============================================================================================#
#Widgets#
#============================================================================================#
root.geometry('1000x600')
x_var = IntVar()
x_motion_label = Label(pos_frame, text='X Motion')
x_fwd = Radiobutton(pos_frame, text='Forwards', variable=x_var, value=1)
x_back = Radiobutton(pos_frame, text='Backwards', variable=x_var, value=-1)
x_distance_entry = Entry(pos_frame)
x_distance_entry_label = Label(
    pos_frame, text='X Distance in cm', width=15, height=2, justify='left')

y_var = IntVar()
y_motion_label = Label(pos_frame, text='Y Motion')
y_up = Radiobutton(pos_frame, text='Up', variable=y_var, value=1)
y_down = Radiobutton(pos_frame, text='Down', variable=y_var, value=-1)
y_distance_entry = Entry(pos_frame)
y_distance_entry_label = Label(
    pos_frame, text='Y Distance in cm', width=15, height=2, justify='left')

theta_var = IntVar()
theta_motion_label = Label(pos_frame, text='Angle')
theta_up = Radiobutton(pos_frame, text='Up', variable=theta_var, value=1)
theta_down = Radiobutton(pos_frame, text='Down', variable=theta_var, value=-1)
theta_angle_entry = Entry(pos_frame)
theta_angle_entry_label = Label(
    pos_frame, text='Theta angle in deg', justify='left')

reset_var = IntVar()
reset_label = Label(pos_frame, text='Reset')
reset_yes = Radiobutton(pos_frame, text='Yes', variable=reset_var, value=1)
reset_no = Radiobutton(pos_frame, text='No', variable=reset_var, value=-1)

submit_button = Button(pos_frame, text='Submit',
                       height=1, width=20, command=submit)
pos_home_button = Button(pos_frame, text='Return to Home Screen',
                         height=1, width=20, command=holder_func)


#============================================================================================#
#Placements#
#============================================================================================#
x_motion_label.grid(row=0, column=0)
x_fwd.grid(row=1, column=0, sticky='W')
x_back.grid(row=2, column=0, pady=(0, 20), sticky='W')
x_distance_entry.grid(row=1, column=1)
x_distance_entry_label.grid(row=1, column=2, padx=(0, 40), sticky='W')

y_motion_label.grid(row=4, column=0)
y_up.grid(row=5, column=0, sticky='W')
y_down.grid(row=6, column=0, pady=(0, 20), sticky='W')
y_distance_entry.grid(row=5, column=1)
y_distance_entry_label.grid(row=5, column=2, sticky='W')

theta_motion_label.grid(row=7, column=0)
theta_up.grid(row=8, column=0, sticky='W')
theta_down.grid(row=9, column=0, pady=(0, 20), sticky='W')
theta_angle_entry.grid(row=8, column=1)
theta_angle_entry_label.grid(row=8, column=2, sticky='W')

reset_label.grid(row=0, column=3)
reset_yes.grid(row=1, column=3, sticky='W')
reset_no.grid(row=2, column=3, sticky='W')

submit_button.grid(row=10, column=0)
pos_home_button.grid(row=10, column=1)

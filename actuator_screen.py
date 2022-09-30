from positioning_screen import *
#from actuator_functions import *
from tkinter import *
import threading
import time
import serial
import math

# root3 = Tk()
# act_frame = Frame(root3)
act_frame = Frame(root, padx=40)
#==================================================#
#Actuator Screen#
#==================================================#


def actuator_display():
    act_freq.grid(row=1, column=3)
    act_amp.grid(row=2, column=3)

    act_freq_label.grid(row=1, column=4)
    act_amp_label.grid(row=2, column=4)

    actuator_on_button.grid(row=1, column=5, sticky='W')
    actuator_off_button.grid(row=2, column=5, sticky='W')


#==================================================#
#Widgets#
#==================================================#
act_freq = Entry(act_frame)
act_amp = Entry(act_frame)
act_freq_label = Label(act_frame, text='Actuator Frequency in Hz')
act_amp_label = Label(act_frame, text='Actuator Amplitude in V')

freq_val = act_freq.get()
amp_val = int(act_amp.get())

act_var = IntVar()
actuator_on_button = Radiobutton(
    act_frame, text='ON', variable=act_var, value=1)
actuator_off_button = Radiobutton(
    act_frame, text='OFF', variable=act_var, value=-1)

#============================================================================================================#
##############################################################################################################
mode = ' '
turn_off_pump = False
frame = Frame(root)
try:
    root.iconbitmap('rainy.ico')
except:
    pass

root.title('All Weather Testing')
board = serial.Serial('COM3', 9600, timeout=1)
time.sleep(0.5)
print('Completed ########################################################################################')


def timer_check(final_time):
    t = 0
    while t < final_time and not turn_off_pump:
        time.sleep(0.05)
        t += 0.05
        frame.update()

#==========================================================#
# Arduino command functions
#==========================================================#


def arduino_timer(time_val, power_int):
    t = 0
    initial_power = power_int
    initial_slider = int(w2.get())
    # board.flush()
    board.write(serial_convert(initial_power))
    board.write(serial_convert(initial_power))
    while not turn_off_pump and t < time_val:
        newSlider = int(w2.get())
        try:
            newPower = int(powerLevel.get())
        except:
            newPower = 0
        time.sleep(0.05)
        t += 0.05
        if newPower != initial_power:
            # board.flush()
            board.write(serial_convert(newPower))
            initial_power = newPower
            w2.set(newPower)
            initial_slider = int(newPower)
        elif newSlider != initial_slider:
            # board.flush()
            board.write(serial_convert(newSlider))
            initial_slider = newSlider
            initial_power = newSlider
            newPower = newSlider
            powerLevel.delete(0, 'end')
            powerLevel.insert(0, str(newSlider))
        opLabel.config(text='Spray running at %s%% power' % (powerLevel.get()))
        frame.update()
    # board.flush()
    board.write(serial_convert(0))


def arduino_oscillate(runTime, restTime, power, oscillations):
    i = 0
    while i < oscillations:
        # board.flush()
        board.write(serial_convert(power))
        timer_check(runTime)
        # board.flush()
        board.write(serial_convert(0))
        timer_check(restTime)
        i += 1


def arduino_constant():
    initial_power = int(powerLevel.get())
    initial_slider = int(w2.get())
    board.write(serial_convert(initial_power))
    board.write(serial_convert(initial_power))  # Not mistake
    while not turn_off_pump:
        newSlider = int(w2.get())
        try:
            newPower = int(powerLevel.get())
        except:
            newPower = 0
        if newPower != initial_power:
            board.write(serial_convert(newPower))
            initial_power = newPower
            w2.set(newPower)
            initial_slider = int(newPower)
        elif newSlider != initial_slider:
            board.write(serial_convert(newSlider))
            initial_slider = newSlider
            initial_power = newSlider
            newPower = newSlider
            powerLevel.delete(0, 'end')
            powerLevel.insert(0, str(newSlider))
        opLabel.config(text='Spray running at %s%% power' % (powerLevel.get()))
        frame.update()
    board.write(serial_convert(0))

#==========================================================#


def forget(frame_in):
    for widgets in frame_in.winfo_children():
        widgets.grid_forget()
        if widgets.winfo_class() == 'Entry':
            widgets.delete(0, 'end')


def shut_off(mode):
    global turn_off_pump
    turn_off_pump = True
    shutoff.grid_forget()
    w2.grid_forget()

#================================================================#
# Start Menu Buttons#
#================================================================#


def pump_start_screen():
    forget(frame)
    global turn_off_pump
    turn_off_pump = False
    # shutoff.deselect()
    start_label.grid(row=0, column=0)
    timer_button.grid(row=1, column=0, sticky='W')
    oscillate_button.grid(row=2, column=0, sticky='W')
    const_button.grid(row=3, column=0, sticky='W')
    topLabel.grid_forget()

    runTime.grid(row=1, column=1)
    restTime.grid(row=2, column=1)
    powerLevel.grid(row=3, column=1)
    oscillation_number.grid(row=4, column=1)

    timeLabel.grid(row=1, column=2)
    restTimeLabel.grid(row=2, column=2)
    powerLabel.grid(row=3, column=2)
    oscillation_number_label.grid(row=4, column=2)

    run_pump_button.grid(row=5, column=1, pady=20)
    home_button.grid(row=6, column=1)


#==========================================================#
# Operating Buttons
#==========================================================#
def run_pump(mode_var):
    match int(mode_var.get()):
        case 1:
            timer()
        case 2:
            oscillate()
        case 3:
            cont()


def timer():
    global mode
    global turn_off_pump
    global pumpIsOn
    turn_off_pump = False
    # shutoff.deselect()
    mode = 'timer'
    time_s = runTime.get()
    powerVal = powerLevel.get()
    time_int = int(time_s)
    power_int = int(powerVal) / 100
    if time_int > 0 and power_int > 0 and power_int <= 100:
        opLabel.config(
            text='Spray running at %s%% power for %s seconds' % (powerVal, time_s))
        shutoff.grid(row=5, column=0)
        w2.set(int(powerVal))
        w2.grid(row=6, column=0)
        frame.update()
        # pumpIsOn = True
        arduino_timer(time_int, power_int)
        # pumpIsOn = False
        shutoff.grid_forget()
        w2.grid_forget()


def cont():
    global mode
    global turn_off_pump
    global pumpIsOn
    turn_off_pump = False
    # shutoff.deselect()
    mode = 'const'
    powerVal = int(powerLevel.get())
    if powerVal > 0 and powerVal <= 100:
        shutoff.grid(row=5, column=0)
        w2.set(int(powerVal))
        w2.grid(row=6, column=0)
        frame.update()
        # pumpIsOn = True
        arduino_constant()
        # pumpIsOn = False
        shutoff.grid_forget()
        w2.grid_forget()


def oscillate():
    global mode
    global turn_off_pump
    global pumpIsOn
    turn_off_pump = False
    mode = 'oscillate'
    time_on = runTime.get()
    time_off = restTime.get()
    powerVal = powerLevel.get()
    time_int = int(time_on)
    rest_int = int(time_off)
    power_int = int(powerVal)
    oscillations_string = oscillation_number.get()
    oscillations = int(oscillations_string)
    if time_int > 0 and rest_int > 0:
        shutoff.grid(row=5, column=0)
        frame.update()
        # pumpIsOn = True
        arduino_oscillate(time_int, rest_int, power_int, oscillations)
        # pumpIsOn = False
        shutoff.grid_forget()


#==========================================================#
# Home Screen Buttons
#==========================================================#
def timer_function():
    runTime.config(state='normal')
    restTime.config(state='disabled')
    oscillation_number.config(state='disabled')


def oscillate_function():
    runTime.config(state='normal')
    restTime.config(state='normal')
    oscillation_number.config(state='normal')


def const_function():
    runTime.config(state='disabled')
    restTime.config(state='disabled')
    oscillation_number.config(state='disabled')

#==========================================================#
# Serial Data Transmission
#==========================================================#


def serial_convert(analogVal):
    analogPower = math.floor(analogVal/100*255)
    num_string = str(analogPower)
    send_string = '<' + num_string + '>'
    send_string = send_string.encode()
    return send_string


#==========================================================#
# All widgets
#==========================================================#
root.geometry('1000x400')
topLabel = Label(frame, text=' ', justify='right')
opLabel = Label(frame, text=' ')
timerLabel = Label(frame, text=' ')
runTime = Entry(frame)
powerLevel = Entry(frame)
timeLabel = Label(frame, text='Run Time in seconds', justify='left')
powerLabel = Label(frame, text='Power level in %', justify='left')
#shutoff = Button(frame, text='Shutoff', padx=50, command=lambda: shut_off(mode), width=10, height=1)
restTime = Entry(frame)
shutoff = Button(frame, text='Shutoff', padx=50,
                 command=lambda: shut_off(mode), width=10, height=1)
restTimeLabel = Label(frame, text='Rest Time in seconds', justify='left')
mode_var = IntVar()
timer_button = Radiobutton(frame, text='Timer Mode',
                           variable=mode_var, value=1, padx=10, command=timer_function)
timer_run_button = Button(frame, text='Run', command=timer, width=10, height=1)
oscillate_button = Radiobutton(frame, text='Oscillation Mode',
                               variable=mode_var, value=2, padx=10, command=oscillate_function)
oscillate_run_button = Button(
    frame, text='Run', command=oscillate, width=10, height=1)
const_button = Radiobutton(frame, text='Constant Operation Mode',
                           variable=mode_var, value=3, padx=10, command=const_function)
const_run_button = Button(frame, text='Run', command=cont, width=10, height=1)
start_label = Label(frame, text='Select Mode')
home_button = Button(frame, text='Return to Home Screen',
                     command=holder_func, width=20, height=1)
oscillation_number = Entry(frame)
oscillation_number_label = Label(
    frame, text='Number of Oscillations', justify='left')
pump_start_screen_button = Button(
    frame, text='Pump Menu', command=pump_start_screen)
w2 = Scale(frame, from_=0, to=100, length=200,
           tickinterval=10, orient=HORIZONTAL)
run_pump_button = Button(frame, text='Run Pump',
                         command=lambda: run_pump(mode_var))
#==========================================================#
# frame.pack()
pump_start_screen()
# act_frame.pack()
actuator_display()


def show_act_screen():
    # frame.grid(row=0, column=0)
    # act_frame.grid(row=0, column=1)
    frame.pack()
    act_frame.pack()

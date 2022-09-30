
import json
import sys
import serial
import serial.tools.list_ports
import scipy
import pandas as pd
import numpy as np
import cv2
import traceback
import time


EXE_ENABLED = False  # Enable for executable version; disable for build version
WAVEFORM_FILE_NAME_EXE = "Waveform_Excel.xlsx"

#WAVEFORM_FILE_NAME_BUILD = "Waveform_Excel_Standard.xlsx"
WAVEFORM_FILE_NAME_BUILD = "Waveform_Excel_Specific.xlsx"

# DUAL_ACTUATOR_SCALER = 0.953 #Scales output voltage for dual setting; configure this based on hardware
DUAL_ACTUATOR_SCALER = 1.0  # No scaling (some hardware doesn't need scaling)
#------------------------------------------------#
# - OTHER SETTINGS -- CHANGE ONLY IF NECESSARY - #
#------------------------------------------------#
MAX_VOLTAGE = 0.8
VOLT_SCALER = 120.0/MAX_VOLTAGE

TEST_TIME = 90000  # milliseconds
if (not EXE_ENABLED):
    TEST_TIME *= 10

EMPTY_WAVEFORM = "0c05000.500.50p010.505050f050050050a0.000.000.001000w0000ff000000ww0aa05000.50"
VERIFY_WAVEFORM = "1c01800.50" + EMPTY_WAVEFORM[10:]
CONNECT_WAVEFORM = "2" + EMPTY_WAVEFORM[1:10]


###########################################################################################################
### TEENSY CONNECTION ###
###########################################################################################################
MANUAL_ATTEMPT = True
TEENSY_CONNECTED = False
TEENSY_SERIAL_PORT = ""
TEENSY_BAUD_RATE = 9600
try:
    TEENSY_SERIAL_PORT = open("COM_PORT.txt").readline()
except:
    TEENSY_SERIAL_PORT = "<NO PORT SELECTED>"
    print("COM_PORT.txt file not found --> No serial port will be selected.")
    MANUAL_ATTEMPT = False

try:  # Manual Connection
    # Intentionally send an error if manual attempt skipped
    if (not MANUAL_ATTEMPT or TEENSY_SERIAL_PORT == ""):
        teensy = serial.Serial(
            port="ERROR",
            baudrate="ERROR"
        )
    print("Attempting manual connection to serial port " +
          TEENSY_SERIAL_PORT + "...")
    teensy = serial.Serial(
        port=TEENSY_SERIAL_PORT,
        baudrate=TEENSY_BAUD_RATE
    )
    teensy.write(EMPTY_WAVEFORM.encode())
    teensy.flush()
    TEENSY_CONNECTED = True
    print("Successfully connected to serial device at " + TEENSY_SERIAL_PORT + ".")
except:  # Automatic Connection
    if (not MANUAL_ATTEMPT or TEENSY_SERIAL_PORT == ""):
        print("No serial port selected. Ignoring manual connection attempt.")
    else:
        print("Manual connection attempt failed.")
    print("\nAttempting automatic connection...")
    myports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
    if (len(myports) == 0):
        print("No serial ports detected.")
        print("Automatic connection attempt failed.")
    else:
        print(str(len(myports)) + " serial port(s) detected:")
        for port in myports:
            print("\t", port)
        port_index = 0
        for port in myports:
            print("\nAttempting connection to " + port[1] + "...")
            port_index += 1

            try:
                teensy = serial.Serial(
                    port=port[0],
                    baudrate=TEENSY_BAUD_RATE
                )  # Send data to device and read back teensy confirmation message
                print("Sending message: " + CONNECT_WAVEFORM)
                teensy.write(CONNECT_WAVEFORM.encode())
                teensy.flush()
                time_out = time.process_time() + .1

                # print(time.process_time())
                # print(time_out)
                # print(time.process_time())
                # time.process_time() <= time_out:
                print(time.process_time())

                if(time.process_time() <= time_out):
                    print("About to execute readline() with process time at " +
                          time.process_time() + " and time out at" + time_out)
                    line = teensy.readline()  # This will be the CONNECT_WAVEFORM string
                else:
                    print("took too long to execute")
                line = teensy.decode()
                line = teensy.restrip()

                print(time.process_time())
                # This will be the actual return message, so this is called twice
                line = teensy.readline().decode().rstrip()

                print("Received message: " + line)
                if (line == "TEENSY CONNECTION CONFIRM" or line.__contains__("Initialization Complete")):
                    TEENSY_CONNECTED = True
                    print("Connection to " + port[1] + " succeeded.")
                    break
                else:
                    print("Connection to " + port[1] + " failed.")
                    if (port_index >= len(myports)-1):
                        print("Automatic connection attempts failed.")
            except:
                print("Connection to " + port[1] + " failed.")
                if (port_index >= len(myports)-1):
                    print("Automatic connection attempts failed.")


###########################################################################################################
### WAVEFORM PARSING FUNCTION ###
###########################################################################################################
def parseWaveforms(sheet, sheet_name, waves, notes, numbers, actFreq, actAmp):
    current_list = []
    num = 0
    temp_num = 0
    note_num = []
    notes_list = []

    actFreq = actFreq
    actAmp = actAmp

    for i in range(len(sheet.index)):
        if (sheet.iloc[num][0] == "Note:"):
            current_note = sheet.iloc[num][1]
            note_num.append(temp_num)
            notes_list.append(current_note)
            num += 1
            continue

        out = "1"

        if (int(sheet.iloc[num][1]) < 0):
            break
        elif (int(sheet.iloc[num][1]) == 0):
            VOLT_SCALER = 120.0/MAX_VOLTAGE
        elif (int(sheet.iloc[num][1]) == 1):
            VOLT_SCALER = 120.0/(MAX_VOLTAGE*DUAL_ACTUATOR_SCALER)

        out += 'c'
        out += str(sheet.iloc[num][1])
        # <-Getting Frequency input from GUI not waveform excel file
        out += str(actFreq).zfill(3)
        # <-Getting Amplitude input from GUI not waveform excel file
        out += "0." + str(int(actAmp/VOLT_SCALER*100)).zfill(2)
        out += "0." + str(int(sheet.iloc[num][4]*100)).zfill(2)

        out += 'p'
        if (int(sheet.iloc[num][5]) < 0):
            out += "010.505050"
        else:
            out += '1'
            out += str(sheet.iloc[num][5])
            out += str(round(sheet.iloc[num][6], 2))
            if (round(sheet.iloc[num][6], 2)*10 % 1 == 0):
                out += '0'
            out += str(sheet.iloc[num][7]).zfill(2)
            out += str(sheet.iloc[num][8]).zfill(2)

        out += 'f'
        if (int(sheet.iloc[num][9]) < 0):
            out += "050050050"
        else:
            if (int(sheet.iloc[num][9]) == 1 or int(sheet.iloc[num][9]) == 3):
                out += '1'
            else:
                out += '0'
            out += str(sheet.iloc[num][10]).zfill(3)
            out += str(sheet.iloc[num][11]).zfill(3)
            out += str(sheet.iloc[num][12]).zfill(2)
            out += str(sheet.iloc[num][13]).zfill(4)

        out += 'a'
        if (int(sheet.iloc[num][9]) < 0):
            out += "0.000.000.001000"
        else:
            if (int(sheet.iloc[num][9]) == 2 or int(sheet.iloc[num][9]) == 3):
                out += '1'
            else:
                out += '0'
            out += "0." + \
                str(int(sheet.iloc[num][14]/VOLT_SCALER*100)).zfill(2)
            out += "0." + \
                str(int(sheet.iloc[num][15]/VOLT_SCALER*100)).zfill(2)

        out += 'w'
        if (int(sheet.iloc[num][16]) < 0):
            out += '0000'
        else:
            out += str(sheet.iloc[num][16]).zfill(4)

        out += 'ff'
        if not (int(sheet.iloc[num][17]) == 1 or int(sheet.iloc[num][17]) == 3
                or int(sheet.iloc[num][17]) == 4 or int(sheet.iloc[num][17]) == 5):
            out += "050000"
        else:
            out += '1'
            out += str(sheet.iloc[num][18]).zfill(2)
            out += str(sheet.iloc[num][19]).zfill(3)

        out += "ww"
        if not (int(sheet.iloc[num][17]) == 4 or int(sheet.iloc[num][17]) == 5):
            out += "00.00"
        else:
            out += "1"
            out += str(sheet.iloc[num][20]).zfill(4)

        out += 'aa'
        if not (int(sheet.iloc[num][17]) == 2 or int(sheet.iloc[num][17]) == 3
                or int(sheet.iloc[num][17]) == 5):
            out += "05000.50"
        else:
            out += '1'
            out += str(sheet.iloc[num][21]).zfill(3)
            out += "0." + \
                str(int(sheet.iloc[num][22]/VOLT_SCALER*100)).zfill(2)

        out += 'wav'
        if (str(sheet.iloc[num][23]) == "-1"):
            out += '0'
        else:
            out += '1'
            out += str(sheet.iloc[num][24]).zfill(4)
            out += str(sheet.iloc[num][23]).upper().rstrip()
            # ^^This isnt last in the Excel sheet because it's a necessary configuration
            # But it should be the last string here because it allows for WAV filenames of various lengths

        num += 1
        current_list.append(out)
        temp_num += 1

    note_num[0] = 0
    note_num.append(temp_num)
    waves[sheet_name] = current_list
    notes[sheet_name] = notes_list
    numbers[sheet_name] = note_num

    print(current_list)

################## Functions needed for Actuator control ##########################

#reset_timer = QTimer()
# reset_timer.setInterval(TEST_TIME)
# reset_timer.timeout.connect(stopWaveform)


def onClicked():
    global MESSAGE_NUMS, TEENSY_CONNECTED
    w = EMPTY_WAVEFORM
    teensy_gui_write(w)
    # reset_timer.start()


def onClicked2(freq, amp):
    global MESSAGE_NUMS, TEENSY_CONNECTED
    w = "1c0"
    w += freq
    w += "0."
    w += str(int(amp/VOLT_SCALER*100)).zfill(2)
    w += "0.-100p010.505050f050050050a0.000.000.001000w0000ff050000ww00.00aa05000.50wav0"
    # print(w)
    teensy_gui_write(w)

    # if (var4 == -1):
    # self.teensy_gui_write(EMPTY_WAVEFORM)
    #  self.reset_timer.stop()
    # elif (var4 == 1):
    #  w = WAVEFORM_STRINGS[SHEET_LIST[self.tabs.currentIndex()-1]][var4]
    #  self.teensy_gui_write(w)
    #  self.reset_timer.start()


def stopWaveform(self):
    global EMPTY_WAVEFORM
    # self.reset_timer.stop()
    self.teensy_gui_write(EMPTY_WAVEFORM)


def teensy_gui_write(waveform_str):
    global TEENSY_CONNECTED, EMPTY_WAVEFORM
    if (TEENSY_CONNECTED):
        try:
            teensy.write(waveform_str.encode())
            teensy.flush()
            if (waveform_str == EMPTY_WAVEFORM):
                print("Waveform Paused")
            elif (waveform_str == VERIFY_WAVEFORM):
                print("Running Verification Waveform")
            else:
                print("Running Waveform: " + waveform_str)
        except:
            print("\nERROR: Cannot write to Teensy.")
            print("RECOMMENDED FIX:")
            print("\t1) Turn off power to the driver.")
            print("\t2) Disconnect, then reconnect the USB cable.")
            print("\t3) Relaunch the GUI.")
            print("\t4) Turn the driver back on when GUI is open.")
            TEENSY_CONNECTED = False
            self.error_msg = MessageBox()
            self.error_msg.setWindowTitle("ERROR")
            self.error_msg.setText("\rCannot write to Teensy\
                  \n\rRECOMMENDED FIX:\
                  \n\r\t1) Turn off power to the driver.\
                  \n\r\t2) Disconnect, then reconnect the USB cable.\
                  \n\r\t3) Relaunch the GUI.\
                  \n\r\t4) Turn the driver back on when the GUI is open.")
########################################################################################


WAVEFORM_FILE_NAME = "Waveform_Excel.xlsx"
if (EXE_ENABLED):
    WAVEFORM_FILE_NAME = WAVEFORM_FILE_NAME_EXE
else:
    WAVEFORM_FILE_NAME = WAVEFORM_FILE_NAME_BUILD

WAVEFORM_CONNECTED = False
MAIN_SHEET_NAME = ""
WAVEFORM_SHEETS = {}
SHEET_LIST = []
WAVEFORM_STRINGS = {}
MESSAGE_NOTES = {}
MESSAGE_NUMS = {}


waveform_file = pd.ExcelFile(WAVEFORM_FILE_NAME)
MAIN_SHEET_NAME = waveform_file.sheet_names[0]
for name in waveform_file.sheet_names:
    SHEET_LIST.append(name)
    sheet = waveform_file.parse(name)
    sheet.fillna(-1, inplace=True)
    sheet = sheet.iloc[2:]
    WAVEFORM_SHEETS[name] = sheet
    #parseWaveforms(sheet, name, WAVEFORM_STRINGS, MESSAGE_NOTES, MESSAGE_NUMS, actFreq, actAmp)
WAVEFORM_CONNECTED = True

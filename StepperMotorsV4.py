###################################
# Actasys						  #
# Python Code for Testing Rig	  #
# Writen by Syed Walid 			  #
# September 2021				  #
###################################

import serial  # For serial communication with arduino
import time
import json
import ast

# Global Variables to keep track of motor positions
xPosition = 0
yPosition = 0
thetaPosition = 0


def executeIns():

    count = 0  # Variable to keep track of how many times while loop is executed

    # txt file that stores the last instructions sent to the motors from the GUI
    f = open("lastInstruction.txt", "r")
    str1 = f.read()  # Reads the instruction in position.txt
    # Places te instruction in dictionary format
    dict1 = ast.literal_eval(str1)
#################################################
    # Port which Arduino is connected to, change based on com_port being used
    serial_port = 'COM3'
#################################################
    baud_rate = 9600  # In arduino, Serial.begin(baud_rate)

    arduino = serial.Serial(serial_port, baud_rate)
    arduino.timeout = 5  # 10 second delay to execute instruction and display position before asking for another set of instruction

    #######################################
    ## Stores the instructions in seperate variables##
    # Variable to store xMotor direction 1->forward -1->backward
    xDirection = dict1['X']
    # Variable to store xMotor distance (0mm-100mm)
    xDistance = dict1['Distance X']

    # Variable to store yMotor direction 1->up -1->down
    yDirection = dict1['Y']
    # Variable to store xMotor distance (0mm-100mm)
    yDistance = dict1['Distance Y']

    # Variable to store thetaMotor direction 1->up -1->down
    thetaDirection = dict1['Actuator Mount']
    # Variable to store xMotor angle (0-360 degrees)
    thetaDistance = dict1['Angle']

    # Variable to store whether to set motor to zero position (1 -> set to zero, -1 -> do nothing>)
    setToZero = dict1['Reset']
    #######################################

    #######################################
    ## Keeps track of all motor positions ##
    global xPosition
    global yPosition
    global thetaPosition

    if(int(xDirection) == 1):
        xPosition = xPosition + int(xDistance)
    elif(int(xDirection) == -1):
        xPosition = xPosition - int(xDistance)

    if(int(yDirection) == 1):
        yPosition = yPosition + int(yDistance)
    elif(int(yDirection) == -1):
        yPosition = yPosition - int(yDistance)

    if(int(thetaDirection) == 1):
        thetaPosition = thetaPosition + int(thetaDistance)
    elif(int(thetaDirection) == -1):
        thetaPosition = thetaPosition - int(thetaDistance)

    # This creates a string with the format <x,x,y,y,t,t,z,xP,yP,tP> to send to arduino
    GUIinstruction = "< %s,%s,%s,%s,%s,%s,%s,%s,%s,%s>" % (
        xDirection, xDistance, yDirection, yDistance, thetaDirection, thetaDistance, setToZero, xPosition, yPosition, thetaPosition)
    print(GUIinstruction)
    # This sets all motor positions back to zero when you reset the motors to zero position
    if(int(setToZero) == 1):
        xPosition = 0
        yPosition = 0
        thetaPosition = 0

    motorPositions = "X Motor: %s mm |Y Motor: %s mm | Theta Motor: %s degrees" % (
        xPosition, yPosition, thetaPosition)
    # post-process or post process

    #######################################
    # This while loops sends the Arduino a string of instruction.
    # The arduino executes istructions and sends back a string of motor positions
    # The motor positions are then stored in current.txt file
    while count < 2:

        motorInstructions = GUIinstruction
        # Encodes the user input and sends it to arduino serial monitor
        arduino.write(motorInstructions.encode())
        time.sleep(1)
        # Arduino sends back message in binary, this converts it back to a string
        output = arduino.readline().decode('ascii')
        # print(output)
        print(motorPositions)

        # Opens current.txt file and writes the current motor positions in the txt file
        with open('current.txt', 'w') as convert_file:
            convert_file.write(json.dumps(motorPositions))

        count += 1  # Counter to make sure the loop only runs 2 times

    #######################################

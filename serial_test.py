import serial
import time

ser = serial.Serial('COM3', 9600, timeout=1)
ser.flush()
print('Delaying 3 seconds')
time.sleep(3)
print('Program Started')
myString = 'H'
encodedString = myString.encode('ascii')

for i in range(0, 8):
    ser.write(b'H')
    print('awake')
    time.sleep(1)
    ser.write(b'L')
    print('sleep')
    time.sleep(1)

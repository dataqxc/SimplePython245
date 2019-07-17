import serial
import keyboard
import time
import sys

#After installing Python, it may be necessary to install following modules under command prompt
#
#    python -m pip install -U pyserial --user
#    python -m pip install -U keyboard --user
#
#This sample program will start DATAQ Instrument usb data acquisition products
#
#The IDE of Python can be found in the Python group, by the name of IDEL
#
#Press key 'x' to EXIT
#since serDataq.readline waits until a line is received, low sample rate makes the program slow in response to key stroke

CONST_SER_PORT = 'COM20'   #get the com port from device manger and enter it here

serDataq = serial.Serial(CONST_SER_PORT, 115200) #DI-245's baud rate is 115200

#for Windows 10, one may run into the exception of "serial.serialutil.SerialException: Cannot configure port, something went wrong. Original message: WindowsError(87, 'Incorrect Parameter.') exception."
#
#Work around until pyserial has fix:, find serialwin32.py inside the folder of c:\users\??? window 10\AppData\Roaming\Python\Python37\site-packages\serial\
#then comment out the following lines in line 219:
#
#    if not win32.SetCommState(self._port_handle, ctypes.byref(comDCB)):
#    raise SerialException(
#        'Cannot configure port, something went wrong. '
#        'Original message: {!r}'.format(ctypes.WinError()))
#
#
#To single step through PY codes, follow
#https://stackoverflow.com/questions/4929251/how-to-step-through-python-code-to-help-debug-issues


serDataq.write(b"S0")        #stop in case device was left scanning
serDataq.write(b"timing 9 7\r")       #refer to protocol for how to change configuration
serDataq.write(b"xrate 1795 200\r")   
serDataq.write(b"chn 0 60416\r")      
serDataq.write(b"S1")           #start scanning
statemachine=0
while True:
    try:
        if keyboard.is_pressed('x'):    #if key 'x' is pressed, stop the scanning and terminate the program
            serDataq.write(b"S0\r")
            time.sleep(1)           
            serDataq.close()
            print("Good-Bye")
            break
        else:
            string = serDataq.read()
            byte=ord(string)
            #print(hex(byte))

            #the following deal with one-channel configuration only, read 245 protocol on how to decode the data stream
            if statemachine==0:
                #wait until we see bit 0=0
                if (byte & 1)==0:
                    data=byte>>1
                    statemachine=1
            else:
                statemachine=0
                if byte & 1:
                    #Second byte, print out raw ADC count
                    data=data+((byte&254)<<6)
                    data=data<<2
                    data=data-32768
                    print(data)
            pass
    except:
        pass

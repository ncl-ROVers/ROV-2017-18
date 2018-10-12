from communication_software.surface_udp import Connection
import time

#Example for running code - I'm not sure exactly how to integrate this with other completed sections
udp = Connection()
udp.connect()
#udp.begin()
udp.begin_console_output() # For debugging only
#udp.output_array[1][1] = 5;

direction = True
value = 1100
while True:
    udp.iterate()
    #Test to turn LED on and off
    time.sleep(1)
    '''if(direction==True):
    value = value + 1
else:
    value = value - 1

udp.set_output_value(7,value)

if(direction==True and value>=1900):
    direction=False
elif(direction==False and value<=1100):
    direction = True'''

    if(udp.output_array[25][1]==0):
        udp.output_array[25][1] = 1
        #udp.output_array[7][1] = 1100
    else:
        udp.output_array[25][1] = 0
        #udp.output_array[7][1] = 1900

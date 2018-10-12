# This program handles the majority of the Raspberry Pi's processing for communication between the surface and ROV
# It's using separate threads for surface-Pi communication and Pi-Arduino communication
# Both threads use the global arrays for inputs and outputs

from threading import Thread
import socket
import serial
import time
class ROVPi():
    def __init__(self):
        # Set up default network details
        self.UDP_RECEIVE_IP = "169.254.116.33"  # The Pi's IP
        self.UDP_RECEIVE_PORT = 5005  # The port we're using
        self.UDP_SEND_IP = "169.254.89.249"  # This needs to be the surface IP (Will be automatically assigned during initial code handshake)
        self.UDP_SEND_PORT = 5005

        self.connect_all_arduinos()
        self.connect_surface()

        # Set up output array initially using received size and labels from the surface
        print("Waiting for array initialisation data from surface.")
        data, addr = self.sock_receive.recvfrom(1024)  # Receive array height
        self.OUTPUT_ARRAY_WIDTH = 3
        self.OUTPUT_ARRAY_HEIGHT = int(data)
        print("Output array is", self.OUTPUT_ARRAY_HEIGHT, "rows tall")
        self.output_array = [[0 for x in range(self.OUTPUT_ARRAY_WIDTH)] for y in range(self.OUTPUT_ARRAY_HEIGHT)]  # define output array
        for i in range(self.OUTPUT_ARRAY_HEIGHT):  # Fill array with string values relating to what each incoming value represents
            data, addr = self.sock_receive.recvfrom(1024)
            self.output_array[i][0] = data.decode("utf-8")
            data, addr = self.sock_receive.recvfrom(1024)
            self.output_array[i][2] = data.decode("utf-8")
            print("Label", str(i), ":", self.output_array[i][0],"Arduino:",self.output_array[i][2])

        # Set up input array initially using received size and labels from the surface
        data, addr = self.sock_receive.recvfrom(1024)  # Receive array height
        self.INPUT_ARRAY_WIDTH = 3
        self.INPUT_ARRAY_HEIGHT = int(data)
        
        self.input_array = [[0 for x in range(self.INPUT_ARRAY_WIDTH)] for y in range(self.INPUT_ARRAY_HEIGHT)]  # define input array
        print("Input array is", self.INPUT_ARRAY_HEIGHT, "rows tall")
        for i in range(self.INPUT_ARRAY_HEIGHT):  # Fill array with string values relating to what each incoming value represents
            print("Waiting for response...")
            data, addr = self.sock_receive.recvfrom(1024)
            self.input_array[i][0] = data.decode("utf-8")
            print("Label", str(i), ":", self.input_array[i][0])
            data, addr = self.sock_receive.recvfrom(1024)
            self.input_array[i][2] = data.decode("utf-8")
            print("Arduino:",self.input_array[i][2])
        
        

    def connect_all_arduinos(self):
        # Set up serial IO for all arduinos
        print("Connecting Arduinos")
        # Check ports 0-9
        self.connect_arduino('/dev/ttyACM0')
        self.connect_arduino('/dev/ttyACM1')
        self.connect_arduino('/dev/ttyACM2')
        self.connect_arduino('/dev/ttyACM3')
        self.connect_arduino('/dev/ttyACM4')
        self.connect_arduino('/dev/ttyACM5')
        self.connect_arduino('/dev/ttyACM6')
        self.connect_arduino('/dev/ttyACM7')
        self.connect_arduino('/dev/ttyACM8')
        self.connect_arduino('/dev/ttyACM9')

    def connect_arduino(self,temp_ser_name):
        print("Identifing",temp_ser_name)
        try:
            temp_ser = serial.Serial(temp_ser_name, 115200)
            temp_ser.timeout = 1
            temp_ser.write(("11011" + "\n").encode("utf-8"))
            letter = temp_ser.readline().decode("utf-8").rstrip()
            if (letter == "A"):
                print("Arduino",temp_ser.name,"is Arduino A")
                self.arduino_a = temp_ser
                print("Arduino A connected:", temp_ser.name)
            elif (letter == "B"):
                print("Arduino",temp_ser.name,"is Arduino B")
                self.arduino_b = temp_ser
                print("Arduino B connected:", temp_ser.name)
            elif (letter == "C"):
                print("Arduino",temp_ser.name,"is Arduino C")
                self.arduino_c = temp_ser
                print("Arduino C connected:", temp_ser.name)
            else:
                if(letter ==""):
                    print("ARDUINO RESPONSE TIMEOUT:", temp_ser.name, "Received ID:",letter, "Retrying")
                    #Recursively retry connection
                    self.connect_arduino(temp_ser_name)
                else:
                    print("UNRECOGNISED ARDUINO:", temp_ser.name, "Received ID:",letter)
        except serial.serialutil.SerialException:
            print("Port",temp_ser_name,"not connected. Continuing.")

    def connect_surface(self):
        # Set up UDP input from surface
        print("Setting up surface->Pi UDP")
        self.sock_receive = socket.socket(socket.AF_INET  # internet
                                     , socket.SOCK_DGRAM)  # UDP
        self.sock_receive.bind((self.UDP_RECEIVE_IP, self.UDP_RECEIVE_PORT))
        print("UDP receiver connected:", self.UDP_RECEIVE_IP, " Port:", self.UDP_RECEIVE_PORT)

        # Set up UDP output to surface
        print("Setting up Pi->surface UDP")
        self.sock_send = socket.socket(socket.AF_INET,  # Internet
                                  socket.SOCK_DGRAM)  # UDP
        print("UDP sender connected:", self.UDP_SEND_IP, " Port:", self.UDP_SEND_PORT)

        # Wait for ping from surface and ping back
        print("Waiting for ping from surface.")
        data, addr = self.sock_receive.recvfrom(1024)  # Read ping
        while (data.decode("utf-8") != "Ready?"):
            print("Data", str(data), "received, but not ping.\r")
            data, addr = self.sock_receive.recvfrom(1024)  # Read ping
        # Get IP from surface
        data, addr = self.sock_receive.recvfrom(1024)  # Read IP
        self.UDP_SEND_IP = data.decode("utf-8")  # Save IP
        print("Ping response received, new SEND_IP is", self.UDP_SEND_IP)
        # Respond to ping and get ready for incoming data
        self.sock_send.sendto(bytes("Ready", "utf-8"), (self.UDP_SEND_IP, self.UDP_SEND_PORT))

    # Reading and writing data to/from the surface via UDP
    def surface_comm(self,thread_name):
        #global output_array  # Allow writing to output_array
        while True:
            # Read surface data
            i = 0
            while i < self.OUTPUT_ARRAY_HEIGHT:
                data, addr = self.sock_receive.recvfrom(1024)
                if ((data.decode("utf-8") == "11111" and i != 0) or (data.decode("utf-8") != "11111" and i == 0)):
                    # If value 11111 found anywhere other than position 0, or position 0 is not 11111, then reset to position 0
                    # This is to avoid writing incorrect values if there are sync issues which would cause erratic behaviour of the ROV
                    print("Data sync error from surface at position", i, ". Current position reset to 0.")
                    i = 0

                if (data.decode("utf-8") == "Ready?"):
                    # If incoming value is the initial ping which suggests the surface code was restarted
                    # Respond to ping and get ready for incoming data
                    print("==========Surface restart detected. Getting ready to receive data.==========")
                    self.sock_send.sendto(bytes("Ready", "utf-8"), (self.UDP_SEND_IP, self.UDP_SEND_PORT))
                    i = 0

                else:
                    self.output_array[i][1] = data.decode("utf-8")  # Update current value in the input array
                    # print((output_array[i][0]), ":", output_array[i][1]) #DEBUG: output received value
                    i += 1  # Increment i
                    # Mark surface connection as being active
                    self.surface_connected = True
            # Send ROV sensor data back to surface
            for i in range(0, self.INPUT_ARRAY_HEIGHT):
                self.sock_send.sendto(bytes(str(self.input_array[i][1]), "utf-8"), (self.UDP_SEND_IP, self.UDP_SEND_PORT))

    # Reading and writing data to/from the Arduino A via USB
    def arduino_comm_a(self, thread_name):
        # global input_array  # Allow writing to input_array
        arduino_id = "A"
        arduino_address = self.arduino_a
        self.generic_arduino_comm(arduino_id, arduino_address)

    # Reading and writing data to/from the Arduino B via USB
    def arduino_comm_b(self, thread_name):
        arduino_id = "B"
        arduino_address = self.arduino_b
        self.generic_arduino_comm(arduino_id, arduino_address)

    # Reading and writing data to/from the Arduino C via USB
    def arduino_comm_c(self, thread_name):
        arduino_id = "C"
        arduino_address = self.arduino_c
        self.generic_arduino_comm(arduino_id, arduino_address)

    def generic_arduino_comm(self, arduino_id, arduino_address):
        # Function to be called by all arduino threads to read and write data to/from arduinos
        port = arduino_address.port
        arduino_address.timeout=0.01
        while True:
            try:
                # Send surface data to arduino
                i = 0
                while i < self.OUTPUT_ARRAY_HEIGHT:
                    # Send to arduino
                    arduino_address.write((str(self.output_array[i][1]) + "\n").encode("utf-8"))
                    i += 1  # Increment i
                    time.sleep(0.001)

                # Get arduino sensor data
                i = 0
                while i < self.INPUT_ARRAY_HEIGHT:
                    # get current value
                    current_value = (arduino_address.readline().decode("utf-8")).rstrip()
                    #if(arduino_id=="A"):
                        #print("Value:",current_value)
                    if(str(self.input_array[i][2]) == arduino_id): # Only write back values if they're assigned to this arduino
                        #print("Pos:",i,"arduinoID",arduino_id)
                        if (int(current_value) == 11111 and i != 0):
                            # If value 11111 found anywhere other than position 0 then reset to position 0
                            # This is to avoid writing incorrect values if there are sync issues which would cause erratic behaviour of the ROV
                            print("Data sync error from Arduino", arduino_id, "at position", i,
                                  ". Current position reset to 0. (Wrong position)")
                            i = 0
                        else:
                            self.input_array[i][1]=int(current_value)
                    elif(i==0):
                        if (int(current_value) != 11111):
                            # If position 0 is not 11111, then reset to position 0
                            # This is to avoid writing incorrect values if there are sync issues which would cause erratic behaviour of the ROV
                            print("Data sync error from Arduino", arduino_id, "at position", i,
                                  ". Current position reset to 0. (Wrong value)")
                            i = 0
                    i += 1  # Increment i

                self.input_array[0][1] = "11111" # Assign sync value for pi-surface communication

                # If this arduino is sending and receiving signals, set the checkbit to 1, else 0
                if(arduino_id=="A"):
                    self.arduino_a_connected = 1
                if (arduino_id == "B"):
                    self.arduino_b_connected = 1
                if (arduino_id == "C"):
                    self.arduino_c_connected = 1
                    
            except serial.SerialException:
                print("Arduino",arduino_id,"not responding. Retrying connection.")
            #except Exception as e: print("Arduino",arduino_id,":",e) #Shh, fail quietly
            except:
                print("Arduino",arduino_id,"timeout. (Feel free to ignore this message)")
                #print("Unknown error in arduinocom")
                #print("Error: Arduino",arduino_id,"lost. Attempting to reconnect on port",port)
                #time.sleep(1)
                #try:
                #    arduino_address = serial.Serial(port, 115200)
                #    arduino_address.timeout = 1
                #except:
                #    print("Arduino",arduino_id," reconnection failed")

    def check_connection(self,thread_name):
        while (True):
            time.sleep(0.5)
            # This function checks if arduinos are connected and functioning
            self.arduino_a_connected = 0
            self.arduino_b_connected = 0
            self.arduino_c_connected = 0
            self.surface_connected = False
            time.sleep(0.5); # Wait for half a second, in which time it should have been overwritten
            # Send checkbits in the sync string
            dig = [[0 for x in range(1)] for y in range(5)]  # define sync array
            dig[0] = self.arduino_a_connected
            dig[1] = self.arduino_b_connected
            dig[2] = self.arduino_c_connected
            #dig[3] = 0  # not assigned
            #dig[4] = 0  # not assigned
            #self.input_array[1][1]=str("".join(str(dig)))
            output = ""
            for i in range (0,3):
                output = output+str(dig[i])
            self.input_array[1][1]=str(output)

            if(self.surface_connected==False):
                # If surface connection lost
                # Cut thrusters power
                for i in range(1, 7):
                    self.output_array[i][1]=1500


    def begin_connection_check(self):
        check_connection = Thread(target=self.check_connection, args=("Thread-6",))
        check_connection.start()

    def print_to_console(self,thread_name):
        while True:
            time.sleep(1)
            print("===RECIEVED SURFACE DATA:===")
            for i in range(self.OUTPUT_ARRAY_HEIGHT):
                print(i, (self.output_array[i][0]), ":", self.output_array[i][1], "(For Arduino",self.output_array[i][2],")")
            print("===RECIEVED ARDUINO DATA:===")
            for i in range(self.INPUT_ARRAY_HEIGHT):
                print(i, (self.input_array[i][0]), ":", self.input_array[i][1], "(From Arduino",self.input_array[i][2],")")

    def begin_arduino_comm(self):
        print("==Starting Arduino A communication stream==")
        arduino_comm_a = Thread(target=self.arduino_comm_a, args=("Thread-2",))
        arduino_comm_a.start()
        print("==Starting Arduino B communication stream==")
        arduino_comm_b = Thread(target=self.arduino_comm_b, args=("Thread-3",))
        arduino_comm_b.start()
        print("==Starting Arduino C communication stream==")
        arduino_comm_c = Thread(target=self.arduino_comm_c, args=("Thread-4",))
        arduino_comm_c.start()

    def begin_surface_comm(self):
        print("==Starting surface communication stream==")
        surface_comm = Thread(target=self.surface_comm, args=("Thread-1",))
        surface_comm.start()

    def begin_console_output(self):
        print_to_console = Thread(target=self.print_to_console, args=("Thread-5",))
        print_to_console.start()



# Define and start threads
pi = ROVPi()
pi.begin_arduino_comm()
pi.begin_surface_comm()
pi.begin_console_output()
pi.begin_connection_check()








import socket
import time
from threading import Thread
from datetime import datetime

class Connection():

    def __init__(self):
        # Define the array to be transferred
        self.OUTPUT_ARRAY_WIDTH = 3 #(Label, Value, ArduinoID)
        self.OUTPUT_ARRAY_HEIGHT = 26
        self.output_array = [[0 for x in range(self.OUTPUT_ARRAY_WIDTH)] for y in range(self.OUTPUT_ARRAY_HEIGHT)]

        # Define the array to be received
        self.INPUT_ARRAY_WIDTH = 3 #(Label, Value, ArduinoID)
        self.INPUT_ARRAY_HEIGHT = 10
        self.input_array = [[0 for x in range(self.INPUT_ARRAY_WIDTH)] for y in range(self.INPUT_ARRAY_HEIGHT)]

        #self.UDP_RECEIVE_IP = "169.254.89.249"  # This needs to be the surface IP
        self.UDP_RECEIVE_IP = socket.gethostbyname(socket.gethostname())  # Automatically retrieved surface IP
        self.UDP_RECEIVE_PORT = 5005  # The port we're using

        self.UDP_SEND_IP = "169.254.116.33"  # The Pi's IP
        self.UDP_SEND_PORT = 5005


        # ========================================================================
        # ==================== Allocate slots for each output ====================
        # ========================================================================
        self.output_array[0][0] = "Synchronisation"  # Top value remains the same at all times
                                                    #  just in case things become unsynchronised
        self.output_array[0][2] = "All"

        # Key:
        # output_array [#][0] = Label
        # output_array [#][2] = Arduino ID

        # Thrusters for general movement
        self.output_array[1][0] = "ForeLeftThruster"
        self.output_array[1][2] = "A"
        self.output_array[2][0] = "ForeRightThruster"
        self.output_array[2][2] = "A"
        self.output_array[3][0] = "TopLeftThruster"
        self.output_array[3][2] = "A"
        self.output_array[4][0] = "TopRightThruster"
        self.output_array[4][2] = "A"
        self.output_array[5][0] = "AftLeftThruster"
        self.output_array[5][2] = "A"
        self.output_array[6][0] = "AftRightThruster"
        self.output_array[6][2] = "A"
        # Camera rotation
        self.output_array[7][0] = "CameraX"
        self.output_array[7][2] = "C"
        self.output_array[8][0] = "CameraY"
        self.output_array[8][2] = "C"
        # Arm A is stepper motor in arm which requires 8 pwm signals
        self.output_array[9][0] = "ArmA1"
        self.output_array[9][2] = "B"
        self.output_array[10][0] = "ArmA2"
        self.output_array[10][2] = "B"
        self.output_array[11][0] = "ArmA3"
        self.output_array[11][2] = "B"
        self.output_array[12][0] = "ArmA4"
        self.output_array[12][2] = "B"
        self.output_array[13][0] = "ArmA5"
        self.output_array[13][2] = "B"
        self.output_array[14][0] = "ArmA6"
        self.output_array[14][2] = "B"
        self.output_array[15][0] = "ArmA7"
        self.output_array[15][2] = "B"
        self.output_array[16][0] = "ArmA8"
        self.output_array[16][2] = "B"
        # Arm B is stepper motor in arm which requires 4 pwm signals
        self.output_array[17][0] = "ArmB1"
        self.output_array[17][2] = "B"
        self.output_array[18][0] = "ArmB2"
        self.output_array[18][2] = "B"
        self.output_array[19][0] = "ArmB3"
        self.output_array[19][2] = "B"
        self.output_array[20][0] = "ArmB4"
        self.output_array[20][2] = "B"
        # Arm C is stepper motor in arm which requires 4 pwm signals
        self.output_array[21][0] = "ArmC1"
        self.output_array[21][2] = "A"
        self.output_array[22][0] = "ArmC2"
        self.output_array[22][2] = "A"
        self.output_array[23][0] = "ArmC3"
        self.output_array[23][2] = "A"
        self.output_array[24][0] = "ArmC4"
        self.output_array[24][2] = "A"
        self.output_array[25][0] = "IndicatorLED"
        self.output_array[25][2] = "All"

        self.output_array[0][1] = 11111  # Synchronisation value is 5 1s

        # =======================================================================
        # ==================== Allocate slots for each input ====================
        # =======================================================================
        self.input_array[0][0] = "Synchronisation"  # Top value remains the same at all times just in case things become unsynchronised
        self.input_array[0][2] = "All"
        self.input_array[1][0] = "Online"  # Check if Arduinos are online
        self.input_array[1][2] = "All"
        # Values from depth sensor
        self.input_array[2][0] = "PressureSensor"
        self.input_array[2][2] = "A"
        self.input_array[3][0] = "TemperatureSensor"
        self.input_array[3][2] = "A"
        self.input_array[4][0] = "DepthSensor"
        self.input_array[4][2] = "A"
        self.input_array[5][0] = "AltitudeSensor"
        self.input_array[5][2] = "A"
        self.input_array[5][0] = "Left arm left switch"
        self.input_array[5][2] = "B"
        self.input_array[5][0] = "Left arm right switch"
        self.input_array[5][2] = "B"
        self.input_array[5][0] = "Right arm left switch"
        self.input_array[5][2] = "B"
        self.input_array[5][0] = "Right arm right switch"
        self.input_array[5][2] = "B"
        # Key:
        # input_array [#][0] = Label
        # input_array [#][2] = Arduino ID

    def connect(self):
        # Set up UDP output to ROV
        print("Setting up Surface->Pi UDP")
        self.sock_send = socket.socket(socket.AF_INET,  # Internet
                                       socket.SOCK_DGRAM)  # UDP
        print("UDP sender connected:", self.UDP_SEND_IP, " Port:", self.UDP_SEND_PORT)


        # Set up UDP input from ROV
        print("Setting up Pi->Surface UDP")
        self.sock_receive = socket.socket(socket.AF_INET,  # internet
                                          socket.SOCK_DGRAM)  # UDP
        self.sock_receive.bind((self.UDP_RECEIVE_IP, self.UDP_RECEIVE_PORT))
        print("UDP receiver connected:", self.UDP_RECEIVE_IP, " Port:", self.UDP_RECEIVE_PORT)

        # Ping Pi software to ensure it's running and everything is fine
        self.sock_send.sendto(bytes("Ready?", "utf-8"), (self.UDP_SEND_IP, self.UDP_SEND_PORT))
        self.sock_send.sendto(bytes(self.UDP_RECEIVE_IP, "utf-8"), (self.UDP_SEND_IP, self.UDP_SEND_PORT)) #Send surface IP so Pi knows where to send data (to avoid needing to set a static ip on the surface computer)
        print("Waiting for response from ROV.")
        data, addr = self.sock_receive.recvfrom(1024)    # Read ping (or any data at all which would indicate that the Pi is online)
        # If the surface has previously sent data then the pi would continue spitting out sensor data despite the surface restarting
        # Therefore any data at all is fine for this check
        print("Response received")

        # Send basic output array data
        self.sock_send.sendto(bytes(str(self.OUTPUT_ARRAY_HEIGHT), "utf-8"), (self.UDP_SEND_IP, self.UDP_SEND_PORT))
        print("Init output array size:", str(self.OUTPUT_ARRAY_HEIGHT))
        for i in range(0, self.OUTPUT_ARRAY_HEIGHT):
            current_value = self.output_array[i][0]
            self.sock_send.sendto(bytes(str(current_value), "utf-8"), (self.UDP_SEND_IP, self.UDP_SEND_PORT))
            print("Sent label: " + str(self.output_array[i][0]))
            current_value = self.output_array[i][2]
            self.sock_send.sendto(bytes(str(current_value), "utf-8"), (self.UDP_SEND_IP, self.UDP_SEND_PORT))
            print("Sent Arduino ref: " + str(current_value))

        # Send basic input array data
        self.sock_send.sendto(bytes(str(self.INPUT_ARRAY_HEIGHT), "utf-8"), (self.UDP_SEND_IP, self.UDP_SEND_PORT))
        print("Init input array size:", str(self.INPUT_ARRAY_HEIGHT))
        for i in range(0, self.INPUT_ARRAY_HEIGHT):
            time.sleep(0.05)
            current_value = self.input_array[i][0]
            self.sock_send.sendto(bytes(str(current_value), "utf-8"), (self.UDP_SEND_IP, self.UDP_SEND_PORT))
            print("Sent label: " + str(self.input_array[i][0]))
            current_value = self.input_array[i][2]
            self.sock_send.sendto(bytes(str(current_value), "utf-8"), (self.UDP_SEND_IP, self.UDP_SEND_PORT))
            print("Sent Arduino ref: " + str(current_value))

    # def begin(self):
    #     print("==Starting UDP communication stream==")
    #     # Create and start threads
    #     rov_comm = Thread(target=self.rov_comm, args=("Thread-1",))
    #     rov_comm.start()
    #     check_connection_ongoing = Thread(target=self.check_connection_ongoing, args=("Thread-3",))
    #     check_connection_ongoing.start()

    def iterate(self):
        # Completes one iteration, to be called on each main clock cycle
        self.send_data()
        self.receive_data()
        return self.check_connection(), self.input_array, self.check_connection_arduino("a"), self.check_connection_arduino("b"), self.check_connection_arduino("c")

    def begin_console_output(self):
        print_to_console = Thread(target=self.print_to_console, args=("Thread-2",))
        print_to_console.start()

    # def rov_comm(self, thread_name):  # All further communication with the ROV is handled in this function
    #     while True:
    #         # Send output array down to ROV
    #         #print("Sending data")
    #         for i in range(0, self.OUTPUT_ARRAY_HEIGHT):
    #             current_value = self.output_array[i][1]
    #             self.sock_send.sendto(bytes(str(current_value), "utf-8"), (self.UDP_SEND_IP, self.UDP_SEND_PORT))
    #
    #         # Get sensor data from ROV
    #         #print("Receiving data")
    #         i = 0
    #         while i < self.INPUT_ARRAY_HEIGHT:
    #             data, addr = self.sock_receive.recvfrom(1024)
    #             #print("Received data:",data.decode("utf-8"),"for position",str(i))
    #             if (data.decode("utf-8") == "11111" and i != 0):
    #                 # If value 11111 found anywhere other than position 0, or position 0 is not 11111, then reset to position 0
    #                 # This is to avoid writing incorrect values if there are sync issues which would cause erratic behaviour of the ROV
    #                 print("Data sync error from ROV at position", i, ". Current position reset to 0. (Wrong position)")
    #                 i = 0
    #             if (data.decode("utf-8") != "11111" and i == 0):
    #                 # If value 11111 found anywhere other than position 0, or position 0 is not 11111, then reset to position 0
    #                 # This is to avoid writing incorrect values if there are sync issues which would cause erratic behaviour of the ROV
    #                 print("Data sync error from ROV at position", i, ". Current position reset to 0. (Wrong number)")
    #                 i = 0
    #             self.input_array[i][1] = int(data.decode("utf-8"))
    #             i += 1  # Increment i

    def send_data(self):
        # Send output array down to ROV
        # Define new string
        data_string = ""
        # For each element in the array
        for i in range(0, self.OUTPUT_ARRAY_HEIGHT):
            # Append this data including index and delimiter in format
            # array_index:value;array_index:value; etc
            # (EG: "0:156;1:51;2:9")
            data_string = str(i)+":"+str(self.output_array[i][1])+";"
        # Send this string to ROV
        self.sock_send.sendto(bytes(str(data_string), "utf-8"), (self.UDP_SEND_IP, self.UDP_SEND_PORT))


    def receive_data(self):
        try:
            # Receive data from the ROV's sensors
            data, addr = self.sock_receive.recvfrom(1024)
            # Split into array of "index:value" strings
            incoming = data.decode("utf-8").split(";")
            # For each incoming value
            for i in range(0,len(incoming)):
                # Split the incoming value into index and value
                index = incoming[i].split(":")[0]
                value = incoming[i].split(":")[1]
                # Set the specified value in the input array
                self.input_array[index][1] = value
            # Set last_updated to now (part of check_connection)
            self.last_updated = datetime.now()
        except (IndexError):
            print("Error receiving data. Array index invalid.")
        except:
            print("Error receiving data. Unknown Error.")

    def check_connection_arduino(self,arduino_id):
        if(len(str(self.get_input_value(1)))!=3): #Ensure the string actually represents the 3 arduinos
            print("Warning: Only",len(str(self.get_input_value(1))),"Arduinos found. Assuming none are connected.")
            return False #Assume it's not connected. At least
        if(arduino_id.lower()=="a"):
            return str(self.get_input_value(1))[2]==1
        elif (arduino_id.lower() == "b"):
            return str(self.get_input_value(1))[1] == 1
        elif (arduino_id.lower() == "c"):
            return str(self.get_input_value(1))[0] == 1

    def check_connection(self):
        # Returns 0 if connection works, -1 if it doesn't
        #if(self.connected==False):
        # If it wasn't updated within the last second, assume the connection dropped
        if ((datetime.now()-self.last_updated).total_seconds() >= 1):
            return True
        else:
            return False

    # def check_connection_ongoing(self, thread_name):
    #     print("Beginning thread to periodically test connection.")
    #     self.connected = False
    #     while(True):
    #         # This function writes a value to input_array which will be overwritten quickly if the Pi is connected
    #         # Returns 0 if connection works, -1 if it doesn't
    #         test_value = 404
    #         # Write 404 to sync value rather than 11111
    #         self.input_array[0][1] = test_value
    #         time.sleep(0.5)  # Wait for half a second, in which time it should have been overwritten
    #         if (self.input_array[0][1] == test_value):
    #             # If not overwritten, then we can assume the connection is lost
    #             self.connected=False
    #         else:
    #             # If it was overwritten, we assume the connection is ongoing
    #             self.connected=True

    def set_output_value(self, index, value):
        # Sets a value for the specified output
        self.output_array[index][1] = int(value)

    def get_output_value(self, index):
        return int(self.output_array[index][1])

    def identify_output(self, index):
        return self.output_array[index][0]

    def identify_input(self, index):
        return self.input_array[index][0]

    def get_input_value(self, index):
        return int(self.input_array[index][1])


    def print_to_console(self, thread_name):
        while True:
            time.sleep(1)
            print("===SENT DATA:===")
            for i in range(self.OUTPUT_ARRAY_HEIGHT):
                print(i, (self.output_array[i][0]),"(", self.output_array[i][2],"):", self.output_array[i][1])
            print("===RECIEVED DATA:===")
            for i in range(self.INPUT_ARRAY_HEIGHT):
                print(i, (self.input_array[i][0]), ":", self.input_array[i][1])


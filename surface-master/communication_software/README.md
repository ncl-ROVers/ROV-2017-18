# Surface communication with the ROV

`surface_udp.py` handles communication between the surface and the ROV. It sets up 2 empty Integer arrays (1 for output values such as thrusters, and 1 for input values such as sensors) where the first columns describe what that value is for.
After initialisation, the code simply updates the values in the second columns of these arrays which represent the ROV's outputs and inputs.

`surface_udp.py` is multithreaded: One thread to communicate with the ROV, as not to disturb any of the other surface code.

## How to initiate this class
### Initialise
- connection = Connection()
- connection.connect()
### To update data (execute on each cycle)
- connection.iterate()

####This returns
- Main connection status
- Array of input values (from sensors)
- Arduino A connection status
- Arduino B connection status
- Arduino C connection status

## How to interact with this class
- void set_output_value(int index, int value) *Set the value of an output (listed below. EG: Thruster)*
- int get_output_value(int index) *Get the current value of an output (listed below. EG: Thruster)*
- string identify_output(int index) *Get the label associated with an output index (EG: 8 = Camera Y)*
- string identify_input(int index) *Get the label associated with an input index (EG: 1 = Online Arduino Check)*
- int get_input_value(int index) *Set the value of an input (listed below. EG: Depth sensor)*
- int check_connection() *Returns 0 for connected, -1 for not*

## Output index <Min value,Max value>
- [0] *Internal use only - Ensures data transmission is syncronised*
- [1] Fore Left Thruster <1100,1900>
- [2] Fore Right Thruster <1100,1900>
- [3] Top Left Thruster <1100,1900>
- [4] Top Right Thruster <1100,1900>
- [5] Aft Left Thruster <1100,1900>
- [6] Aft Right Thruster <1100,1900>
- [7] Camera X <1100,1900>
- [8] Camera Y <1100,1900>
- [9] Left Arm Motor 0 (Stepper closest to body) <-1000,1000>
- [10] Left Arm Motor 1 <-1000,1000>
- [11] Left Arm Motor 2 <-1000,1000>
- [12] Left Arm Motor 3 (Grabber) <-1000,1000>
- [13] Right Arm Motor 0 (Stepper closest to body) <-1000,1000>
- [14] Right Arm Motor 1 <-1000,1000>
- [15] Right Arm Motor 2 <-1000,1000>
- [16] Right Arm Motor 3 (Grabber) <-1000,1000>
- [17] ArmL0 Step boundary (Stepper closest to body) <1,1000>
- [18] ArmL1 Step boundary <1,1000>
- [19] ArmL2 Step boundary <1,1000>
- [20] ArmL3 Step boundary (Gripper) <1,1000>
- [21] ArmR0 Step boundary (Stepper closest to body) <1,1000>
- [22] ArmR1 Step boundary <1,1000>
- [23] ArmR2 Step boundary <1,1000>
- [24] ArmR3 Step boundary (Gripper) <1,1000>
- [25] Indication LED - pin 13 on Arduino <0,1>

## Input index
- [0] *Internal use only - Ensures data transmission is syncronised*
- [1] Online Arduino Check *(CBA so 111 = all online, 000 = all offline, 001 only A online)*
- [2] Pressure sensor
- [3] Temperature sensor
- [4] Depth sensor
- [5] Altitude sensor
- [6] Left Arm Left Switch
- [7] Left Arm Right Switch
- [8] Right Arm Left Switch
- [9] Right Arm Right Switch

## View the camera feed
To view the 1080p camera feed in a web browser, go to http://169.254.116.33:8081/stream_simple.html
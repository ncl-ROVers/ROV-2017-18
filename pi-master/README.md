# Raspberry Pi

`main.py` handles all communication between the surface and the arduino. It sets up 2 empty arrays (1 for output values such as thrusters, and 1 for input values such as sensors) where the first columns describe what that value is for.
These arrays are initiated with data coming from the surface (The size of the arrays and the contents of the first column).
After this initialisation, the code simply updates the values in the second columns of these arrays; sending the input data back to the surface, and the output data to the Arduino.

`main.py` is multithreaded: one thread communicating with the surface, and another with the arduino.

`main.py` must start running on the Pi before the surface code is run.

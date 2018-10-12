# Arudino Readme

## Introduction

The main function of the ROV is to produce PWM signals to various actuators on the ROV. The values of the signals to output are communicated by UART interface from a Raspberry PI.

## PWM
The Arduino lists itself as having 13 PWM pins; upon testing it was found that most of these can be controlled and set to the values in the range for the main thruster motor.  
Here is an introduction on PWM and creating PWM signals in Arudinos: https://www.arduino.cc/en/Tutorial/SecretsOfArduinoPWM

## Sending and receiving data to/from arduino
Each Arduino has two Integer arrays. `outputArray` is for data from the surface to control the arduino outputs. `inputArray` is data from the Arduino's sensors to be sent back up to the surface.
The sizes of these arrays needs to be hardcoded with the current implementation.

In both arrays, position 0 should always be 11111. This helps re-synchronise the data in transmission should any packets be lost etc.

## Using multiple Arduinos
The `main` code has been depricated and should be used as a template for new Arduinos.
Now each Arduino has its own file, with a variable called `arduinoID` which is a string which holds a single capital letter (A/B/C etc) identifying the arduino. The Raspberry Pi code can then modify the references to assign the right inputs and outputs to the correct Arduino.
To find out which arduino is which, the Pi code will send a string `"ping"` and will get a letter in string format in response.

## Arduino A
### Outputs
Thrusters require signals between 1100 and 1900ms.
- [2] Fore Left Thruster
- [3] Fore Right Thruster
- [4] Top Left Thruster
- [5] Top Right Thruster
- [6] Aft Left Thruster
- [7] Aft Right Thruster
- [13] Indication LED
### Inputs
- [20] Depth sensor 3 (White wire)
- [21] Depth sensor 2 (Green wire)


## Arduino B
### Outputs
### Inputs

## Arduino C
### Outputs
2 Servos to control camera rotation.
- [1] CameraX
- [2] CameraY
- [13] Indication LED
### Inputs
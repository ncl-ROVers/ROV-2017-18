#include <MS5837.h>

#include <WString.h>
#include <Servo.h>
#include <Wire.h>
#include "MS5837.h"

// This is Arduino A
String arduinoID = "A";

//For communication
String incomingString = "";
const int OUTPUT_ARRAY_SIZE = 26;
const int INPUT_ARRAY_SIZE = 6;
int outputArray[OUTPUT_ARRAY_SIZE];     //Array received from the Pi to control all outputs
int inputArray[INPUT_ARRAY_SIZE];     //Array of currently measured input values to send back to Pi
int arrayPointer=0;              // Int to point to current array position
String inputString = "";         // a String to hold incoming data
boolean stringComplete = false;  // whether the string is complete
boolean sendComplete = true;   // Set to false once the full output array has been received, set back to true once full input array has been sent
boolean execute = false;  // Only do the rest of the code if not received ping
boolean pause = false; // Pause data reading until back in sync after reading sensors (Avoids values being assigned wrongly)


// the following variable is a long because the time, measured in miliseconds,
// will quickly become a bigger number than can be stored in an int.
unsigned long previousMillis = 0;        // will store last time servo values updated
long interval = 1;           // interval at which to update servo (milliseconds)

// the following variable is a long because the time, measured in miliseconds,
// will quickly become a bigger number than can be stored in an int.
unsigned long previousMillisRead = 1000;        // will store last time values updated
long intervalRead = 500;           // interval at which to read sensors (milliseconds)


MS5837 sensor; // Depth sensor object


//For thrusters
#define SERVO_COUNT 10 // 6 Thrusters, 4 other pwm signals

// 1500ms +/- 400ms
#define SERVO_MIN_PERIOD_MUS 1100
#define SERVO_MAX_PERIOD_MUS 1900

#define FORE_TOP_INDEX_1 0
#define FORE_TOP_INDEX_2 1
#define FORE_LEFT_INDEX 2
#define FORE_RIGHT_INDEX 3
#define AFT_LEFT_INDEX 4
#define AFT_RIGHT_INDEX 5

byte servoMappings [] = {2,3,4,5,6,7,8,9,10,11};
Servo servo[SERVO_COUNT];


void setup() {
  Serial.begin(115200);     // opens serial port, sets data rate to 115200 bps
  Serial.setTimeout(30);     //The default timeout is a second - way too slow for our purposes. Now set to 1ms
  inputString.reserve(200); // reserve 200 bytes for the inputString
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);

  inputArray[0]=11111; //Synchronisation value just in case one value is lost in action 

  //For thrusters
  for (size_t i = 0; i < SERVO_COUNT; i++) {
        servo[i].attach(servoMappings[i], SERVO_MIN_PERIOD_MUS, SERVO_MAX_PERIOD_MUS);
        // send "stop" signal to ESC.
        servo[i].writeMicroseconds(1500);
    }
    // delay to allow the ESC to recognize the stopped signal
    delay(1000);

// Depth sensor setup
// Initialize pressure sensor
  // Returns true if initialization was successful
  // We can't continue with the rest of the program unless we can initialize the sensor

// Commented out for debugging
  
//  while (!sensor.init()) {
//    Serial.println("Init failed!");
//    Serial.println("Are SDA/SCL connected correctly?");
//    Serial.println("Blue Robotics Bar30: White=SDA, Green=SCL");
//    Serial.println("\n\n\n");
//    delay(1000);
//  }
//  
//  sensor.setModel(MS5837::MS5837_30BA);
//  sensor.setFluidDensity(997); // kg/m^3 (freshwater, 1029 for seawater)


// Set default output values for connected pwm devices to disable them on boot
for(size_t i = 1; i < 25; i++){
    outputArray[i]= 1500;}
}

void loop() {
//==============================================COMMUNICATION===========================================
  //-----------------------------Check for incoming "output" values (eg: Thrusters)------------------------
  if (stringComplete) { //If new value received (ending in a newline character)
  //------------------------------------Check if the Pi wants the ID---------------------------------
    

    int currentValue = inputString.toInt();
    int pingValue = 11011;
    if(currentValue==pingValue){
      //If "ping" string received, respond with which arduino this is (A,B,C etc)
      Serial.println(arduinoID);
      //Reset input string and wait for new input
      inputString = "";
      stringComplete = false;
      sendComplete = true;
      //Continue to next loop iteration
      execute = false; //Don't run the code for a ping command
    }
    else{
      execute = true; //Assume you want to run the code
    }
//    else{
//      Serial.println("output was ");
//      Serial.println(currentValue);
//      Serial.println(" Not ");
//      Serial.println(pingValue);
//    }
    if(arrayPointer==0&&currentValue!=11111){
      //Reset input string and wait for new input
      inputString = "";
      stringComplete = false;
    }
    else{
    if(execute){
      
      if(currentValue == 11111 && arrayPointer != 0){
        arrayPointer = 0; //If sync value is not in position 0, reset to position 0
        //Serial.print("Sync error. Now reset to position 0."); //FOR DEBUGGING ONLY
      }
      
      outputArray[arrayPointer]= currentValue;
  
      if (arrayPointer==(OUTPUT_ARRAY_SIZE-1)){
        arrayPointer = 0; //Reset arraypointer if it's reached the maximum array position
        sendComplete = false; //Send back input values once all output values have been received
      }
      else{
        arrayPointer = arrayPointer + 1; //Else increment arrayPointer
      }
  
      //Reset input string and wait for new input
      inputString = "";
      stringComplete = false;
    }
    }
  }
  //------------------------------------Send input values back to Pi---------------------------------
  if (!sendComplete && execute){ //If ready to send back values
    sendInputs();
  }
//==============================================/COMMUNICATION===========================================

//==============================================READ_SENSORS===========================================

// Only reading every 500 ms to allow the sensors to be read properly
    // check current time
    unsigned long currentMillisRead = millis();
    if(currentMillisRead - previousMillisRead > intervalRead && arrayPointer==OUTPUT_ARRAY_SIZE-1) {
    // save the last time you ran the code
      previousMillisRead = currentMillisRead;

      sensor.read(); // THIS TAKES TOO LONG TO RUN
      inputArray[2]=sensor.pressure();
      inputArray[3]=sensor.temperature();
      inputArray[4]=sensor.depth();
      inputArray[5]=sensor.altitude();
      //inputArray[5]++; // For testing only

      // To prevent values becoming out of sync
      // Wait 30ms to ensure all output values would have been sent
      // (Each value has a delay of 1ms so this compensates for a max of 30 values)
      //delay(30);
      // Send back input values so the pi will be ready to resend output values
      sendInputs();
      // Reset array pointer since we'll restart reading from 0
      arrayPointer=0;
    }

//==============================================/READ_SENSORS===========================================

//==============================================CONTROL_OUTPUTS===========================================

// Indication LED for testing
  if(outputArray[25]==1){
      digitalWrite(LED_BUILTIN, HIGH);
    }
    else{
      digitalWrite(LED_BUILTIN, LOW);
    }


// Only changing pwm every 1 ms to allow the servos/thrusters to read them properly
    // check current time
    unsigned long currentMillis = millis();
    if(currentMillis - previousMillis > interval) {
    // save the last time you ran the code
      previousMillis = currentMillis;   
      for(size_t i = 0; i < SERVO_COUNT; i++) { //Pins 0 - servo_count-1
        if(i<6){ // If it's a thruster then 
          setServo(outputArray[i+1], i); //Set thrusters to the correct levels from array index 1-6
        }
        else{
          setServo(outputArray[i+15], i); //Set the 4 arm pwm values
        }
          
      }
      
    }

  
 //==============================================/CONTROL_OUTPUTS===========================================

}

// Method to return the array of inputs back to the pi
void sendInputs(){
  for(int i=0; i<INPUT_ARRAY_SIZE; i++) {
      Serial.println(inputArray[i]);      
      //Serial.println("11111");  
    }
    sendComplete = true;
}


/*
  SerialEvent occurs whenever a new data comes in the hardware serial RX. This
  routine is run between each time loop() runs, so using delay inside loop can
  delay response. Multiple bytes of data may be available.
*/
void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read();
    // add it to the inputString:
    inputString += inChar;
    // if the incoming character is a newline, set a flag so the main loop can
    // do something about it:
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
}

//Control servos/thrusters and cap value to correct range
inline void setServo(int value, int servoIndex) {
    if (value <= SERVO_MIN_PERIOD_MUS) {
        value = SERVO_MIN_PERIOD_MUS;
    }
    if (value >SERVO_MAX_PERIOD_MUS) {
        value =SERVO_MAX_PERIOD_MUS;
    }
    servo[servoIndex].writeMicroseconds(value);
}

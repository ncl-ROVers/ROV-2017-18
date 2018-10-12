#include <WString.h>
#include <Servo.h>

// This is Arduino A
String arduinoID = "A";

//For communication
String incomingString = "";
const int OUTPUT_ARRAY_SIZE = 10;
const int INPUT_ARRAY_SIZE = 1;
int outputArray[OUTPUT_ARRAY_SIZE];     //Array received from the Pi to control all outputs
int inputArray[INPUT_ARRAY_SIZE];     //Array of currently measured input values to send back to Pi
int arrayPointer=0;              // Int to point to current array position
String inputString = "";         // a String to hold incoming data
boolean stringComplete = false;  // whether the string is complete
boolean sendComplete = false;   // Set to false once the full output array has been received, set back to true once full input array has been sent

//For thrusters
#define SERVO_COUNT 6

// 1500ms +/- 400ms
#define SERVO_MIN_PERIOD_MUS 1100
#define SERVO_MAX_PERIOD_MUS 1900

#define FORE_TOP_INDEX_1 0
#define FORE_TOP_INDEX_2 1
#define FORE_LEFT_INDEX 2
#define FORE_RIGHT_INDEX 3
#define AFT_LEFT_INDEX 4
#define AFT_RIGHT_INDEX 5

byte servoMappings [] = {0,1,2,3,4,5};
Servo servo[SERVO_COUNT];


void setup() {
  Serial.begin(115200);     // opens serial port, sets data rate to 115200 bps
  Serial.setTimeout(1000);     //The default timeout is a second - way too slow for our purposes. Now set to 1ms
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
}

void loop() {
//==============================================COMMUNICATION===========================================
  //-----------------------------Check for incoming "output" values (eg: Thrusters)------------------------
  if (stringComplete) { //If new value received (ending in a newline character)

    if(inputString.equals("ping")){
      //If "ping" string received, respond with which arduino this is (A,B,C etc)
      Serial.println(arduinoID);
      //Reset input string and wait for new input
      inputString = "";
      stringComplete = false;
      sendComplete = true;
      //Continue to next loop iteration
      continue;
    }
    
    int currentValue = inputString.toInt();

    
    
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

  //------------------------------------Send input values back to Pi---------------------------------
  if (!sendComplete){ //If ready to send back values
    for(int i=0; i<INPUT_ARRAY_SIZE; i++) {
      Serial.println(inputArray[i]);      
    }
    sendComplete = true;
  }
//==============================================/COMMUNICATION===========================================

//==============================================READ_SENSORS===========================================



//==============================================/READ_SENSORS===========================================

//==============================================CONTROL_OUTPUTS===========================================

  if(outputArray[9]==1){
      digitalWrite(LED_BUILTIN, HIGH);
    }
    else{
      digitalWrite(LED_BUILTIN, LOW);
    }
    
 for (size_t i = 0; i < SERVO_COUNT; i++) {
        setServo(inputArray[i+1], i); //Set thrusters to the correct levels
    }

  
 //==============================================/CONTROL_OUTPUTS===========================================

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

#ifndef _PINS_
#define _PINS_

#include <Servo.h>

#define SERVO_COUNT 6

// 1500ms +/- 400ms
#define SERVO_MIN_PERIOD_MUS 1100
#define SERVO_MAX_PERIOD_MUS 1900

#define FORE_TOP_INDEX 0
#define FORE_TOP_INDEX 1
#define FORE_LEFT_INDEX 2
#define FORE_RIGHT_INDEX 3
#define AFT_LEFT_INDEX 4
#define AFT_RIGHT_INDEX 5

// byte servoMappings [] = {0,1,2,3,4,5};
Servo servo[SERVO_COUNT];


void setup() {
    for (size_t i = 0; i < SERVO_COUNT; i++) {
        servo[i].attach(servoMappings[i], SERVO_MIN_PERIOD_MUS, SERVO_MAX_PERIOD_MUS);
        // send "stop" signal to ESC.
        servo[i].writeMicroseconds(1500);
    }
    // delay to allow the ESC to recognize the stopped signal
    delay(1000);
}

void loop() {
    // Set signal value, which should be between 1100 and 1900
    // int signal = 1700;

    // Send signal to ESC.
    // servo[0].writeMicroseconds(signal);

    for (size_t i = 0; i < SERVO_COUNT; i++) {
        setServo(SERVO_MIN_PERIOD_MUS, i);
    }
    delay(2);

    for (size_t i = 0; i < SERVO_COUNT; i++) {
        setServo(SERVO_MAX_PERIOD_MUS, i);
    }
    delay(2);
}

inline void setServo(uint value, uint servoIndex) {
    if (value <= SERVO_MIN_PERIOD_MUS) {
        value = SERVO_MIN_PERIOD_MUS;
    }
    if (value >SERVO_MAX_PERIOD_MUS) {
        value =SERVO_MAX_PERIOD_MUS;
    }
    servo[servoIndex].writeMicroseconds(value);
}
#endif

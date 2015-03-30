#include <Practicum.h>

extern "C" {
#include "usbdrv.h"
}

#define RQ_SET_LED    0
#define RQ_GET_SWITCH 1
#define RQ_GET_LIGHT  2

//////////////////////////////////////////////////////////////////////
usbMsgLen_t usbFunctionSetup(uint8_t data[8])
{
  usbRequest_t *rq = (usbRequest_t*)data;
  // static uint8_t switch_state;  /* must stay when usbFunctionSetup returns */
  // static uint16_t light_state;

    uint8_t pwm = rq->wValue.bytes[0]; // 0-255
    uint8_t motor = rq->wIndex.bytes[0]; // 00 01 11 10

    digitalWrite(PIN_PC1, motor/2%2); // motor MSB
    digitalWrite(PIN_PC3, motor%2); // motor LS
    analogWrite(PIN_PC5, pwm); // motor PWM

    return 0;

}

//////////////////////////////////////////////////////////////////////
void setup()
{
    pinMode(PIN_PC1, OUTPUT);
    pinMode(PIN_PC3, OUTPUT);
    pinMode(PIN_PC5, OUTPUT);
    pinMode(PIN_PD3, OUTPUT);
    usbInit();

    /* enforce re-enumeration of USB devices */
    usbDeviceDisconnect();
    delay(300);
    usbDeviceConnect();
}

void loop()
{
  usbPoll();
  // delay(200);
  // digitalWrite(PIN_PD3, 1);
  // delay(100);
  // digitalWrite(PIN_PD3, 0);
}
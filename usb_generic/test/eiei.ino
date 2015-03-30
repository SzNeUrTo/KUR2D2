#include <Practicum.h>
 
void setup()
{
	  pinMode(PIN_PD3, OUTPUT);
	    Serial.begin(9600);
}
 
void loop()
{
	  Serial.println("Hello, Serial");
	    PORTD ^= (1<<PD3);
		  delay(500);
}

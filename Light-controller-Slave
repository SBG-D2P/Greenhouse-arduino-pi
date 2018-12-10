
//--------------------------------------ledStates used to set the LEDs--------------------------------
int RelayState_OFF = LOW;             
int RelayState_ON = HIGH;
//----------------------------------------------------------------------------------------------------

//--------------------------------------PINS-SETUP-RELAY-PAIRS----------------------------------------
int SensorPin = A0; // set input at pin A0
int SensorPin2 = A1;
int Relay1 = 11;  //output pin for relays
int Relay2 = 12;
//----------------------------------------------------------------------------------------------------
 

//---------------------------------------function-#1-TURN-ON------------------------------------------
void TurnON(int& x,uint16_t& y,int& z, int& w, uint16_t& v, uint16_t& t, int& u, uint16_t& o, uint16_t& s){  //relay1, sensorvalue, sensorpin, relay2, relaystastus, sensorvalue2, sensor2
if (v == 0) {                                                       //if relays is off and fine
       digitalWrite(x, RelayState_ON);
       v = 1;
       delay(100);
       y = 0;
                    for (int a=0; a < 5; a = a +1) {//takes average of several measurements
                    y = analogRead(z) + y;
                    }
                    y = y / 5;
                    s = y;
                    delay(100);
                    if ( y < 300 ) {// if current is not flowing then turn off relay and activate second one
                              digitalWrite(x, RelayState_OFF);
                              delay(100);
                              digitalWrite(w, RelayState_ON);
                              o = 1;        // indicates relay2 is ON
                              v = 3;        // change parameter to broken coil relay1
                    }
}

else if (v == 1){                                       //if relay fails midway 
                        digitalWrite(x, RelayState_OFF);
                        v = 3;        // change parameter to broken coil relay1
                        digitalWrite(w, RelayState_ON);
                        o = 1;             // indicates relay2 is ON
  
}

else if (v == 3){                   // coil broken for relay1
        digitalWrite(w, RelayState_ON);
        o = 1;
       delay(100);
       t = 0;
                    for (int a=0; a < 5; a = a +1) {//takes average of several measurements
                    t = analogRead(u) + t;
                    }
                    
                    t = t / 5;
                    delay(100);
                    if ( t < 300 ) {// if current is not flowing then turn off relay and activate second one
                              o = 3;        // change parameter to broken coil relay2
                              digitalWrite(w, RelayState_OFF);
                    }
  
}

else if (v == 2){                   // contact fused for relay1
        digitalWrite(w, RelayState_OFF);
        o = 0;
       delay(100);
       t = 0;
                    for (int a=0; a < 5; a = a +1) {//takes average of several measurements
                    t = analogRead(u) + t;
                    }
                    
                    t = t / 5;
                    delay(100);
                    if ( t > 300 ) {// if current is not flowing then turn off relay and activate second one
                              o = 2;        // change parameter to fused contacts relay2
                    }
}
}
//-----------------------------------------------------------------------------------------------------

//--------------------------------------------function-#2-TURN-OFF------------------------------------
void TurnOFF(int& x,uint16_t& y,int& z, int& w, uint16_t& v, uint16_t& t, int& u, uint16_t& o, uint16_t& s){ //relay1, sensorvalue, sensorpin, relay2, relaystastus, sensorvalue2, sensor2

if ( v == 1){
       digitalWrite(x, RelayState_OFF);
       v = 0;
       delay(100);
       y = 0;
                    for (int a=0; a < 5; a = a +1) {//takes average of several measurements, compensate for oscillating nature of the sensor's input
                    y = analogRead(z) + y;
                    }
                    y = y / 5;
                    if ( y > 300 ) {// if current is flowing then turn off relay and activate second one
                              v = 2;          //change parameer to fused contact relay1
                              digitalWrite(w, RelayState_ON); 
                              o = 1;          //indicate relay2 is ON

                              t = 0;
                              for (int a=0; a < 5; a = a +1) {//takes average of several measurements
                                          t = analogRead(u) + t;
                              }
                    
                              t = t / 5;
                              delay(100);
                              if ( t < 300 ) {// if current is not flowing then turn off relay and activate second one
                              o = 2;        // change parameter to broken coil
                              }
                    }
}

else if (v == 2){
       digitalWrite(w, RelayState_ON);
       o = 1;
       t = 0;
       for (int a=0; a < 5; a = a +1) {//takes average of several measurements
                    t = analogRead(u) + t;
                    }
                    
                    t = t / 5;
                    delay(100);
                    if ( t < 300 ) {// if current is not flowing then turn off relay and activate second one
                              o = 2;        // change parameter to broken coil relay2
                    }
}

else if (v == 3){
       digitalWrite(w, RelayState_OFF);
       o = 0;
       t = 0;
       for (int a=0; a < 5; a = a +1) {//takes average of several measurements
                    t = analogRead(u) + t;
                    }
                    
                    t = t / 5;
                    delay(100);
                    if ( t > 300 ) {// if current is not flowing then turn off relay and activate second one
                              o = 3;        // change parameter to fused contacts relay2
                    }
}
}
//-------------------------------------------------------------------------------------------------------

//-------------------------------------Setup-of-parameter-for-modbus-----------------------------------
uint16_t au16data[16] = {                            // data array for modbus network sharing
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, -1 }; //last two entries must remain 1 and -1 for code to run properly
// {py ON/Off, SensorValue, SensorValue2, Relay1Status, Relay2Status,

#include <ModbusRtu.h>
 
/**
 *  Modbus object declaration
 *  u8id : node id = 0 for master, = 1..247 for slave
 *  u8serno : serial port (use 0 for Serial)
 *  u8txenpin : 0 for RS-232 and USB-FTDI 
 *               or any pin number > 1 for RS-485
 */
Modbus slave(1,0,3); // this is slave 1 and RS-485 on pin 3
//-----------------------------------------------------------------------------------------------------

//---------------------------------------------SETUP-----------------------------------------------------
void setup() {
  slave.begin( 19200 ); // baud-rate at 19200
  pinMode(Relay1, OUTPUT);
  pinMode(Relay2, OUTPUT);
  pinMode(SensorPin, INPUT);
  pinMode(SensorPin2, INPUT);

au16data[1] = 0;  //SensorValue - set initial variable for current detector
au16data[2] = 0;  //SensorValue2 - set initial variable for current detector
au16data[3] = 0;  //Relay1Status - 0 means OFF, 1 means ON, 2 means FAILED-fused, 3 means FAILED-coil
au16data[4] = 0;  //Relay1Status2 - 0 means OFF, 1 means ON, 2 means FAILED-fused, 3 means FAILED-coil
  
}
//-----------------------------------------------------------------------------------------------------


//===============================================MAIN LOOP=============================================
void loop() {
  
slave.poll( au16data, 16 );

for (int a=0; a < 5; a = a +1) {                      //Measure both sensor 
        au16data[1] = analogRead(SensorPin) + au16data[1];
}
au16data[1] = au16data[1] /5;

for (int a=0; a < 5; a = a +1) {
        au16data[2] = analogRead(SensorPin2) + au16data[2];
}
au16data[2] = au16data[2] /5;

                  //au16data[9] = au16data[1];
                  //au16data[10] = au16data[2];

if ((au16data[0] == 1) && (((au16data[1] < 300) && (au16data[2] < 300)) ^ ((au16data[1] > 300) && (au16data[2] > 300))) ) {
                  au16data[1] = 0;
                  au16data[2] = 0;
                  TurnON(Relay1, au16data[1], SensorPin, Relay2, au16data[3], au16data[2], SensorPin2, au16data[4], au16data[9]); // keeps lights on
}


else if ((au16data[0] == 2) && (((au16data[1] < 300) && (au16data[2] > 300)) ^ ((au16data[1] > 300) && (au16data[2] < 300))) ){
                  au16data[1] = 0;
                  au16data[2] = 0;
                  TurnOFF(Relay1, au16data[1], SensorPin, Relay2, au16data[3], au16data[2], SensorPin2, au16data[4], au16data[9]); // keeps lights off
}
  
}
//=============================================================================================================================

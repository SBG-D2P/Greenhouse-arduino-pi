//--------------------------------------ledStates used to set the LEDs--------------------------------
int OFF = LOW;             
int ON = HIGH;
//----------------------------------------------------------------------------------------------------

//--------------------------------------PINS-SETUP-RELAY-PAIRS----------------------------------------
int First = A0; // set input at pin A0
int Second = A1;

int Layer1 = 0;
int SensorSoil[16];

int S0 = 10;   //output pin for demux control
int S1 = 11;
int S2 = 12;  
int S3 = 13;
int E = 9;

int SS0 = 8;   //output pin for demux control
int SS1 = 7;
int SS2 = 6;  
int SS3 = 5;
int E2 = 4;

int Selector[] = {S0, S1, S2, S3};

//----------------------------------------------------------------------------------------------------

//------------------------------------------SETUP-FOR-DEMUX-------------------------------------------

int DEMUX[16][4] = { {OFF, OFF, OFF, OFF}
,{ON, OFF, OFF, OFF}
,{OFF, ON, OFF, OFF}
,{ON, ON, OFF, OFF}
,{OFF, OFF, ON, OFF}
,{ON, OFF, ON, OFF}
,{OFF, ON, ON, OFF}
,{ON, ON, ON, OFF}
,{OFF, OFF, OFF, ON}
,{ON, OFF, OFF, ON}
,{OFF, ON, OFF, ON}
,{ON, ON, OFF, ON}
,{OFF, OFF, ON, ON}
,{ON, OFF, ON, ON}
,{OFF, ON, ON, ON}
,{ON, ON, ON, ON}
};
//------------------------------------------------------------------------------------------------------

//-----------------------------------------------Plugged------------------------------------------------
int Sensors[16];
void Plugged()
{
for (int i = 0; i < 16; ++i) {

    digitalWrite(S0, DEMUX[i][0]);
    digitalWrite(S1, DEMUX[i][1]);
    digitalWrite(S2, DEMUX[i][2]);
    digitalWrite(S3, DEMUX[i][3]);
    digitalWrite(E, LOW);
    delay(10);
    Layer1 = analogRead(First);
    //Serial.println(Layer1);
    delay(10);
    
    if (Layer1 > 300) {
        Sensors[i] = 1;
    }

    else {Sensors[i] = 0;}
    digitalWrite(E, HIGH);
    delay (10);
}


}
//------------------------------------------------------------------------------------------------------

//-------------------------------------------Measuring--------------------------------------------------
void Measuring(){
for (int i = 0; i < 16; ++i) {
      if (Sensors[i] == 1) {

            for (int k = 0; k < 16; ++k) {

            digitalWrite(E2, HIGH);
            digitalWrite(SS0, DEMUX[k][0]);
            digitalWrite(SS1, DEMUX[k][1]);
            digitalWrite(SS2, DEMUX[k][2]);
            digitalWrite(SS3, DEMUX[k][3]);
            digitalWrite(E2, LOW);
            
            delay(10);
            SensorSoil[k] = analogRead(Second);
            //Serial.println(Layer1);
            delay(10);
            }
      }
for (int i = 0; i < 16; ++i) {
Serial.print(SensorSoil[i]);
}
Serial.println(" ");

}

}
//-----------------------------------------------------------------------------------------------------

//-------------------------------------Setup-of-parameter-for-modbus-----------------------------------
uint16_t au16data[16] = {                            // data array for modbus network sharing
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, -1 }; //last two entries must remain 1 and -1 for code to run properly
// {

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

//-------------------------------------------------SETUP-----------------------------------------------
void setup()
{
 pinMode(S0, OUTPUT);
  pinMode(S1, OUTPUT);
  pinMode(S2, OUTPUT);
  pinMode(S3, OUTPUT);
  pinMode(E, OUTPUT);
  pinMode(First, INPUT);

  pinMode(SS0, OUTPUT);
  pinMode(SS1, OUTPUT);
  pinMode(SS2, OUTPUT);
  pinMode(SS3, OUTPUT);
  pinMode(E2, OUTPUT);
  pinMode(Second, INPUT);

  Serial.begin(9600);
  slave.begin( 19200 ); // baud-rate at 19200

  au16data[1] = 0;  //SensorValue - set initial variable for current detector
  au16data[2] = 0;  //SensorValue2 - set initial variable for current detector
  au16data[3] = 0;  //Relay1Status - 0 means OFF, 1 means ON, 2 means FAILED-fused, 3 means FAILED-coil
  au16data[4] = 0;  //Relay1Status2 - 0 means OFF, 1 means ON, 2 means FAILED-fused, 3 means FAILED-coil
  }
//-----------------------------------------------------------------------------------------------------



//=============================================Main-Loop===============================================
void loop()
{

slave.poll( au16data, 16 );
Plugged();
Measuring();

}
//=====================================================================================================



#include "DHT.h"
#define DHTPIN 2 //arduino pin that connected to the DATA pin of DHT
#define DHTTYPE DHT22 //type of DHT used

DHT dht (DHTPIN, DHTTYPE);

float h; //stores humidity value
float t; //store temperature value


//-------------------------------------Setup-of-parameter-for-modbus-----------------------------------
uint16_t au16data[16] = {                            // data array for modbus network sharing
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, -1
}; //last two entries must remain 1 and -1 for code to run properly
// {[0]checkpoint, [1]mode on arduino, [2]ID of probe being red, [3]Value being red, [4]which detectors plugged,

#include <ModbusRtu.h>

/**
    Modbus object declaration
    u8id : node id = 0 for master, = 1..247 for slave
    u8serno : serial port (use 0 for Serial)
    u8txenpin : 0 for RS-232 and USB-FTDI
                 or any pin number > 1 for RS-485
*/
Modbus slave(2, 0, 3); // this is slave 2 and RS-485 on pin 3 (and pin 4 for RE)
//-----------------------------------------------------------------------------------------------------

//--------------------------------------States-used-for-DEMUX-----------------------------------------
int OFF = LOW;
int ON = HIGH;
//----------------------------------------------------------------------------------------------------

//--------------------------------------PINS-SETUP-RELAY-PAIRS----------------------------------------
int SensorPin = A1; // sensor pin for incoming data

int Measurement = 0;//value used to see if sensors are plugged and to gather data

int S0 = 5;   //output pin for demux control of the moiture detection (remote demux on the probe)
int S1 = 6;
int S2 = 7;
int S3 = 8;
//int Enable = 4;// pin to enable the whole system via PNP transistor(shift register and probes)

int TwoDDataArray[16][16];//array to store data from all measured sensors
//uint16_t TwoDDataArray[16];

//----------------------------------------------------------------------------------------------------

//------------------------------------------SETUP-FOR-DEMUX-------------------------------------------
int DEMUX[16][4] = { // change order to match physical 1,2,3...
  {OFF, OFF, OFF, OFF}
  , {ON, OFF, OFF, OFF}
  , {OFF, ON, OFF, OFF}
  , {ON, ON, OFF, OFF}
  , {OFF, OFF, ON, OFF}
  , {ON, OFF, ON, OFF}
  , {OFF, ON, ON, OFF}
  , {ON, ON, ON, OFF}
  , {OFF, OFF, OFF, ON}
  , {ON, OFF, OFF, ON}
  , {OFF, ON, OFF, ON}
  , {ON, ON, OFF, ON}
  , {OFF, OFF, ON, ON}
  , {ON, OFF, ON, ON}
  , {OFF, ON, ON, ON}
  , {ON, ON, ON, ON}
};
//------------------------------------------------------------------------------------------------------

//-------------------------------------SETUP-FOR-SHIFT-REGISTER-----------------------------------------
int latchPin = 11;//change pin number
int dataPin = 9;//change pin number
int clockPin = 10;//change pin number
int SREnable = 12;// shift register enable

int SR1[] = {255, 255, 255, 255, 255, 255, 255, 255, 255, 254, 253, 251, 247, 239, 223, 191, 127,0};  //binary number to select single channel to not be equal to 1 (e.g. 110111) for first shift register
int SR2[] = {255, 254, 253, 251, 247, 239, 223, 191, 127, 255, 255, 255, 255, 255, 255, 255, 255,0};  //idem for second shift register. (will overflow-cascade into the other one)

//int SR1[] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 4, 8,16,32,64,128,0};  //binary number to select single channel to not be equal to 1 (e.g. 110111) for first shift register
//int SR2[] = {0, 1, 2, 4, 8,16,32,64,128, 0, 0, 0, 0, 0, 0, 0, 0,0};  //idem for second shift register. (will overflow-cascade into the other one)


//------------------------------------------------------------------------------------------------------

//-------------------------------------FUNCTION-FOR-SHIFT-REGISTER--------------------------------------
void ShiftOut(int g)//change g accordingly here "uint16_t& x"
{
  digitalWrite(SREnable, LOW);
  delay(10);
  digitalWrite(latchPin, LOW);
  delay(100);
  shiftOut(dataPin, clockPin, MSBFIRST, SR1[g]);
  delay(5);
  shiftOut(dataPin, clockPin, MSBFIRST, SR2[g]);
  delay(5);
  digitalWrite(latchPin, HIGH);
  delay(100);
  
}
//------------------------------------------------------------------------------------------------------

//-----------------------------------------------Plugged------------------------------------------------
void Plugged()
{
  au16data[4] = 0;//storing which probes are plugged in in a "binary" fashion 1 == only first; 9 == first and third (0000000000000101) I think negative is for the last one
digitalWrite(SREnable, LOW);
    ShiftOut(0);// disable all probes before setting demux to I0 (LED)
    delay(10);
    digitalWrite(S0, DEMUX[0][0]);
    digitalWrite(S1, DEMUX[0][1]);
    digitalWrite(S2, DEMUX[0][2]);
    digitalWrite(S3, DEMUX[0][3]);
    delay(10);
  
  for (int i = 0; i < 17; ++i) {// loops through probes

    ShiftOut(i);
    delay(100);
    int Measurement = analogRead(SensorPin);
    delay(100);
    
    if (Measurement > 450) { // adds probe to binary list if there was current flowing (present value is 630 mV with setup)
    
      au16data[4] = au16data[4] + round(pow(2, i));// adds probe to number in binary form needs rounding otherwise returns too small value from floating point
      au16data[5] = Measurement;
    }
    delay (10);
  }
 au16data[1] = 0;
 ShiftOut(0);
 digitalWrite(SREnable, HIGH);
 
}
//------------------------------------------------------------------------------------------------------

//-------------------------------------------Measuring--------------------------------------------------
void Measuring(uint16_t& p) {
  int x = p;//converting modbus uint16 to int for functions
  
  for (int k = 0; k < 16; ++k) {    //getting measurment on all 16 levels of the probe

    digitalWrite(S0, DEMUX[k][0]);
    digitalWrite(S1, DEMUX[k][1]);
    digitalWrite(S2, DEMUX[k][2]);
    digitalWrite(S3, DEMUX[k][3]);
    ShiftOut(x);

    delay(10);  //delay to let pads electrify properly
    int Measurement = analogRead(SensorPin); //measure voltage
    ShiftOut(0);
    TwoDDataArray[x][k] = Measurement; //storing data in main array
    //slave.poll( au16data, 16 ); //put 40 miliseconds delay in the pythonscript
    delay(5);
  }
   au16data[1] = 0;
 
}
//-----------------------------------------------------------------------------------------------------

//---------------------------------------------Data-Transfert------------------------------------------
void DataTransfert(uint16_t& x, uint16_t& z, uint16_t& y) {  
  digitalWrite(SREnable, HIGH);
  delay(10);
  //for (uint16_t i = 0; i < 16; i++) { //loops through all values of a given probe
    //z = TwoDDataArray[x][i];
    z = TwoDDataArray[x][y];
  //}
  au16data[1] = 0;
}
//-----------------------------------------------------------------------------------------------------

//-----------------------------------------------Indicator---------------------------------------------
/*void Indicator(uint16_t& x)
{
    ShiftOut(0);
    digitalWrite(S0, DEMUX[0][0]);
    digitalWrite(S1, DEMUX[0][1]);
    digitalWrite(S2, DEMUX[0][2]);
    digitalWrite(S3, DEMUX[0][3]);
  
    int Indicates = x; 
    Indicates = (Indicates - SR1[0]);
    ShiftOut(Indicates);     
      // keep function for later reference Indicates[j] = bitRead(num, j);  

  
  for (int i = 0; i < 16; ++i) {// loops through probes needing water
    if (Indicates[i] == 1){

    digitalWrite(E, HIGH);
    digitalWrite(S0, DEMUX[i][0]);
    digitalWrite(S1, DEMUX[i][1]);
    digitalWrite(S2, DEMUX[i][2]);
    digitalWrite(S3, DEMUX[i][3]);
    
    digitalWrite(E, LOW);// flash idicator light
    delay(500);
    digitalWrite(E, HIGH);
    delay (500);
    digitalWrite(E, LOW);
    delay(500);
    digitalWrite(E, HIGH);
    }
  }
 digitalWrite(E, HIGH);
}*/
//------------------------------------------------------------------------------------------------------

//-------------------------------------------------SETUP-----------------------------------------------
void setup()
{


  pinMode(S0, OUTPUT);
  pinMode(S1, OUTPUT);
  pinMode(S2, OUTPUT);
  pinMode(S3, OUTPUT);
  pinMode(SensorPin, INPUT);

  pinMode(dataPin, OUTPUT);
  pinMode(clockPin, OUTPUT);
  pinMode(latchPin, OUTPUT);

  //ShiftOut(0);
  digitalWrite(SREnable, HIGH);
  slave.begin( 19200 ); // baud-rate at 19200
   dht.begin(); //begin the sensor 

  //Plugged();//check which probes are plugged when device is started or reseted --  must be last line of setup
}
//-----------------------------------------------------------------------------------------------------



//=============================================Main-Loop===============================================
void loop()
{
  //ShiftOut(0);
  digitalWrite(SREnable, HIGH);
  delay(10);
  slave.poll( au16data, 16 );

  if (au16data[1] == 0) {
    delay(5);
    return;
  }

  else if (au16data[1] == 1) {
    Plugged();
  }

  else if (au16data[1] == 2) {
    Measuring(au16data[2]);// ID of probe being red
  }

  else if (au16data[1] == 3) {
    DataTransfert(au16data[2], au16data[3], au16data[7]);//(Probe being red, Value(level) being red, Indicates which level to read)
  }

 /* else if (au16data[1] == 4) {
    Indicator(au16data[8]);
  }*/
  else if (au16data[1] == 5) {
  au16data[5] = ((dht.readTemperature())*10);
  au16data[6] = dht.readHumidity();
  }
}
//=====================================================================================================

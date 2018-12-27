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
Modbus slave(2, 0, 3); // this is slave 2 and RS-485 on pin 3
//-----------------------------------------------------------------------------------------------------

//--------------------------------------States-used-for-DEMUX-----------------------------------------
int OFF = LOW;
int ON = HIGH;
//----------------------------------------------------------------------------------------------------

//--------------------------------------PINS-SETUP-RELAY-PAIRS----------------------------------------
int Second = A1; // sensor pin for incoming data

int Layer2 = 0;//value used to see if sensors are plugged and to gather data

int S0 = 10;   //output pin for demux control of the probe (probe selector)
int S1 = 11;
int S2 = 12;
int S3 = 13;
int E = 9;

int SS0 = 5;   //output pin for demux control of the moiture detection (remote demux on the probe)
int SS1 = 6;
int SS2 = 7;
int SS3 = 8;
int E2 = 4;

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

//-----------------------------------------------Plugged------------------------------------------------
void Plugged()
{
  au16data[4] = 0;//storing which probes are plugged in in a "binary" fashion 1 == only first; 9 == first and third (0000000000000101) I think negative is for the last one

    digitalWrite(E2, HIGH);
    digitalWrite(SS0, DEMUX[0][0]);
    digitalWrite(SS1, DEMUX[0][1]);
    digitalWrite(SS2, DEMUX[0][2]);
    digitalWrite(SS3, DEMUX[0][3]);
    digitalWrite(E2, LOW);
  
  for (int i = 0; i < 16; ++i) {// loops through probes
    
    digitalWrite(E, HIGH);
    digitalWrite(S0, DEMUX[i][0]);
    digitalWrite(S1, DEMUX[i][1]);
    digitalWrite(S2, DEMUX[i][2]);
    digitalWrite(S3, DEMUX[i][3]);
    digitalWrite(E, LOW);
    delay(10);
    
    delay(5);

    if (Layer2 > 350) { // adds probe to binary list if there was current flowing
      //au16data[4] = Layer1;
      au16data[4] = au16data[4] + round(pow(2, i));// adds probe to number in binary form needs rounding otherwise returns too small value from floating point
    }
    digitalWrite(E, HIGH);
    delay (5);
  }
 digitalWrite(E2, HIGH);
 au16data[1] = 0;
}
//------------------------------------------------------------------------------------------------------

//-------------------------------------------Measuring--------------------------------------------------
void Measuring(uint16_t& p) {
  int x = p;
  digitalWrite(E, HIGH);        //Selecting desired probe out of 16
  digitalWrite(S0, DEMUX[x][0]);
  digitalWrite(S1, DEMUX[x][1]);
  digitalWrite(S2, DEMUX[x][2]);
  digitalWrite(S3, DEMUX[x][3]);
  //digitalWrite(E, LOW);

  for (int k = 0; k < 16; ++k) {    //getting measurment on all 16 levels of the probe

    digitalWrite(E2, HIGH);
    digitalWrite(SS0, DEMUX[k][0]);
    digitalWrite(SS1, DEMUX[k][1]);
    digitalWrite(SS2, DEMUX[k][2]);
    digitalWrite(SS3, DEMUX[k][3]);
    digitalWrite(E, LOW);
    digitalWrite(E2, LOW);

    delay(10);  //delay to let pads electrify properly
    //TwoDDataArray[x][k] = analogRead(Second); //storing data in main array
    int Layer2 = analogRead(Second);
    TwoDDataArray[x][k] = Layer2; //analogRead(Second); //storing data in main array
    //slave.poll( au16data, 16 ); //put 40 miliseconds delay in the pythonscript
  
    delay(5);
  }
   au16data[1] = 0;
   digitalWrite(E, HIGH);
   digitalWrite(E2, HIGH);
}
//-----------------------------------------------------------------------------------------------------

//---------------------------------------------Data-Transfert------------------------------------------
void DataTransfert(uint16_t& x, uint16_t& z, uint16_t& y) {  
  //for (uint16_t i = 0; i < 16; i++) { //loops through all values of a given probe
    //z = TwoDDataArray[x][i];
    z = TwoDDataArray[x][y];
  //}
  au16data[1] = 0;
}
//-----------------------------------------------------------------------------------------------------

//-------------------------------------------------SETUP-----------------------------------------------
void setup()
{
  pinMode(S0, OUTPUT);
  pinMode(S1, OUTPUT);
  pinMode(S2, OUTPUT);
  pinMode(S3, OUTPUT);
  pinMode(E, OUTPUT);

  pinMode(SS0, OUTPUT);
  pinMode(SS1, OUTPUT);
  pinMode(SS2, OUTPUT);
  pinMode(SS3, OUTPUT);
  pinMode(E2, OUTPUT);
  pinMode(Second, INPUT);

  digitalWrite(E, HIGH);
  digitalWrite(E2, HIGH);

  slave.begin( 19200 ); // baud-rate at 19200

  Plugged();//check which probes are plugged when device is started or reseted --  must be last line of setup
}
//-----------------------------------------------------------------------------------------------------



//=============================================Main-Loop===============================================
void loop()
{

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
}
//=====================================================================================================




//////////////////////  Global Variables /////////////////////////

//----- Pump Parameters -------//
const int modePin = 12;
const int pump = 11;
int state;
int dataIn;
boolean runNow;


const byte numCharsP = 32;
char receivedCharsP[numCharsP];

boolean newPump = false;


//----- Actuator Positioning Parameters -------//
int xdriverPUL = 7;    //Linear Motor Driver PUL- connected to pin d7
int xdriverDIR = 6;    //Linear Motor Driver DIR- connected to pin d6

int ydriverPUL = 9;    //Linear Motor Driver PUL- connected to pin d9
int ydriverDIR = 8;    //Linear Motor Driver DIR- connected to pin d8

int thetaIN1 = 2;      //Theta Motor Driver IN1 - connected to pin d2
int thetaIN2 = 3;      //Theta Motor Driver IN2 - connected to pin d3
int thetaIN3 = 4;      //Theta Motor Driver IN3 - connected to pin d4
int thetaIN4 = 5;      //Theta Motor Driver IN4 - connected to pin d5

//----- X-Y Motor properties-------//
const double  stepperLength = 100;                              // Total mm Range of Motor Movement (max is 100 mm)
int travelPerRev = 2;                                           // (mm)
int pulsePerRev = 400;                                          // (microstep/revolution)
long totalStep = (stepperLength / travelPerRev) * pulsePerRev;  // (microsteps) total steps needed for full range

//-------- Theta Motor properties ----------//
int degree = 360;         // Total degree range of of motor movement (max is 720 degrees)
int steps = 2038;         // Total steps needed for full range 2038

//-------- XTurn Funtion -----------//
boolean one;
int xMove = 0;  // mm increments 
int dir = 0;    // Drection (1 to mover to the right -1 to move to the left)

//-------- YTurn Funtion -----------//
boolean two;
int yMove = 0;   // mm increments 
int ydir = 0;    // Drection (1 to mover to the right -1 to move to the left)

//-------- ThetaTurn Funtion -----------//
boolean three;
int thetaMove = 0;   // (Angle) Degree increments 
int thetadir = 0;    // Drection (1 to mover to the up -1 to move to the down)


//------- To get user input & execute instructions -------//
const byte numChars = 64;
char receivedChars[numChars];        // array used to store user data 
char tempChars[numChars];            // temporary array for use when parsing
char rcArray[64];                    // array used to store python instruction string converted to chars  

char messageFromPC[numChars] = {0};  // variables to hold the parsed data

int direcX = 0;       // variables to hold the parsed data (direcXtion for XMotor)
int distanceX = 0;    // variables to hold the parsed data (distance for XMotor)

int direcY = 0;       // variables to hold the parsed data (direction for YMotor)
int distanceY = 0;    // variables to hold the parsed data (distance for YMotor)

int direcTheta = 0;   // variables to hold the parsed data (direction for ThetaMotor)
int angle = 0;        // variables to hold the parsed data (degree for ThetaMotor)

int resetMotor = 0;   // Variable to hold instruction on whether to set motor to zero position 

//int savePosition = 0; // Variable to hold instrcution on whether to save position to EEPROM 

boolean newData = false;  // variable to check/set if user data is being inputed in the serial monitor 

//-------- Motor positions --------//
int xPosition = 0;    // Used to display motor locaions and set to zero position
int yPosition = 0;
int thetaPosition = 0;

//////////////////////////////////////////////////////////////////

#include <AccelStepper.h>

int motorInterfaceType = 1; // motor interface type set to 1 when using a motor driver
AccelStepper xMotor = AccelStepper(motorInterfaceType, xdriverPUL, xdriverDIR);
AccelStepper yMotor = AccelStepper(motorInterfaceType, ydriverPUL, ydriverDIR);

#define stepsPerRevolution  4
AccelStepper thetaMotor = AccelStepper(stepsPerRevolution, thetaIN1, thetaIN3, thetaIN2, thetaIN4); // Pins entered in sequence IN1-IN3-IN2-IN4 for proper step sequence

//////////////// SetUp Fuction ///////////////////////
void setup() {

  Serial.begin(9600);
  Serial.flush();

  pinMode (modePin, OUTPUT);
  pinMode(pump, OUTPUT);
  pinMode(13, OUTPUT);
  digitalWrite(13, LOW);
  
  pinMode(xdriverPUL, OUTPUT);
  pinMode(xdriverDIR, OUTPUT);
  
  pinMode(ydriverPUL, OUTPUT);
  pinMode(ydriverDIR, OUTPUT);

  pinMode(thetaIN1, OUTPUT);
  pinMode(thetaIN2, OUTPUT);
  pinMode(thetaIN3, OUTPUT);
  pinMode(thetaIN4, OUTPUT);

  //Set max speed, speed, and acceleration of xMotor
  xMotor.setMaxSpeed(4000);
  xMotor.setSpeed(3000);
  xMotor.setAcceleration(4000);
  //Set max speed, speed, and acceleration of yMotor
  yMotor.setMaxSpeed(4000);
  yMotor.setSpeed(3000);
  yMotor.setAcceleration(4000);
  //Set max speed, speed, and acceleration of thetaMotor
  thetaMotor.setMaxSpeed(1000);
  thetaMotor.setAcceleration(50);
  thetaMotor.setSpeed(700);
  
}
//////////////////////////////////////////////////////

/////////////////// Main Loop ////////////////////////
void loop() {

runNow = true;
//while (runNow == true) {
while (!Serial.available()){
  // do nothing
  }
  digitalWrite(pump, HIGH);
  if (Serial.read() == 'A') {
    state = 1;
    runNow = false;
  }
  else if (Serial.read() == 'P') { 
    state = 0;
    runNow = false;
  }
  delay(1000);
  digitalWrite(pump, LOW);
//}
 while (state == 0) {
  //while (true){
    recvWithStartEndMarkers();
  }
 //}
 if (state == 1){
  recvMotorInstruction();                //runs function to receive user instructions
    if (newData == true) 
    {
        strcpy(tempChars, receivedChars); // this temporary copy is necessary to protect the original data because strtok() used in parseData() replaces the commas with \0
         
        parseData();                      //runs functions to break user input into parts
        execInstructions();               //runs function to use user data to execute instructions (TurnX TurnY TurnTheta function)
        displayPosition();
        
        newData = false;        
    }
 }
 digitalWrite(13, HIGH);
 delay(1000);
 digitalWrite(13, LOW);  
}
//////////////////////////////////////////////////////

/////////// Function to Move X-Motor in Specified distanceX & direcXtion   ///////////////
void TurnX(int MoveOne, int direcX)
{
  int mov = map(MoveOne, 0, stepperLength, 0, totalStep);
  if(direcX == 1)
  {
    xMotor.move(mov);
    one = 0;
    while( one == 0)
    {
      if(xMotor.distanceToGo() != 0)
      {
        xMotor.run();
      }
      else
      {
        one = 1;
      }
    }
  }
  else if(direcX == -1)
  {
    xMotor.move(-mov);
    one = 0;
    while( one == 0)
    {
      if(xMotor.distanceToGo() != 0)
      {
        xMotor.run();
      }
      else
      {
        one = 1;
      }
     }
  }
}
/////////////////////////////////////////////////////////////////////////////////////

/////////// Function to Move Y-Motor in Specified distance & direction   ////////////
void TurnY(int MoveOne, int direcY)
{
  int mov = map(MoveOne, 0, stepperLength, 0, totalStep);
  if(direcY == 1)
  {
    yMotor.move(mov);
    two = 0;
    while( two == 0)
    {
      if(yMotor.distanceToGo() != 0)
      {
        yMotor.run();
      }
      else
      {
        two = 1;
      }
    }
  }
  else if(direcY == -1)
  {
    yMotor.move(-mov);
    two = 0;
    while( two == 0)
    {
      if(yMotor.distanceToGo() != 0)
      {
        yMotor.run();
      }
      else
      {
        two = 1;
      }
     }
  }
}
///////////////////////////////////////////////////////////////////////////////////////

/////////// Function to Move Theta-Motor to a specified angle & direction   ////////////
void TurnTheta(int MoveOne, int direcTheta)
{
  int mov = map(MoveOne, 0,degree, 0,steps);   // Stepper motor rotates 720 degrees when it takes 2038 steps 
  if(direcTheta == -1)
  {
    thetaMotor.move(mov);
    three = 0;
    while( three == 0)
    {
      if(thetaMotor.distanceToGo() != 0)
      {
        thetaMotor.run();
      }
      else
      {
        three = 1;
      }
    }
  }
  else if(direcTheta == 1)
  {
    thetaMotor.move(-mov);
    three = 0;
    while( three == 0)
    {
      if(thetaMotor.distanceToGo() != 0)
      {
        thetaMotor.run();
      }
      else
      {
        three = 1;
      }
     }
  }
}
////////////////////////////////////////////////////////////////////////////////////

//////////////// Function to get instruction from Python /////////////////////////
void recvMotorInstruction() {
    
    char startMarker = '<';
    char endMarker = '>';

    while (Serial.available() > 0 && newData == false) {

      String inPythonData = Serial.readStringUntil('\n'); //recieves a string from python

      inPythonData.toCharArray(rcArray,64);               //store string into array of chars

      //Loop to remove '<''>' markers from the array 
      for(int i = 0; i < 64; i++)
      {
        if(rcArray[i+1] == endMarker){
          receivedChars[i] = '\0';
          newData = true;
          break;
        }
        else if (rcArray[i+1] != endMarker)
        {
          receivedChars[i] = rcArray[i+1];
        }
      } 

    }
}
/////////////////////////////////////////////////////////////////////

///////////////// Function to split user input //////////////////////
void parseData() {                       // split the data into its parts

    char * strtokIndx;                   // this is used by strtok() as an index
 
    strtokIndx = strtok(tempChars, ","); // this continues where the previous call left off
    direcX = atoi(strtokIndx);          //  X MotorDirection, convert this part to an integer
    strtokIndx = strtok(NULL, ",");
    distanceX = atoi(strtokIndx);        // X Motor Distance, convert this part to an integer

    strtokIndx = strtok(NULL, ",");      
    direcY = atoi(strtokIndx);            //Y Motor Direction
    strtokIndx = strtok(NULL, ",");
    distanceY = atoi(strtokIndx);         //Y Motor Distance

    strtokIndx = strtok(NULL, ",");
    direcTheta = atoi(strtokIndx);        //Theta Motor Direction
    strtokIndx = strtok(NULL, ",");
    angle = atoi(strtokIndx);             //Theta Motor Distance (Angle)

    strtokIndx = strtok(NULL, ",");    
    resetMotor = atoi(strtokIndx);        //Reset Instruction

    strtokIndx = strtok(NULL, ",");    
    xPosition = atoi(strtokIndx);         //X Motor Position
    strtokIndx = strtok(NULL, ",");    
    yPosition = atoi(strtokIndx);         //Y Motor Position 
    strtokIndx = strtok(NULL, ",");    
    thetaPosition = atoi(strtokIndx);     //Theta Motor Position

}
/////////////////////////////////////////////////////////////////////

////////////// Function to execute specified instructions ////////////////////
void execInstructions() {

    dir = direcX;
    xMove = distanceX;

    ydir = direcY;
    yMove = distanceY;

    thetadir = direcTheta;
    thetaMove = angle;    // Angle increments 
    
    TurnX(xMove, dir);
    TurnY(yMove, ydir);
    TurnTheta(thetaMove, thetadir);

    setToZeroPosition();

}
/////////////////////////////////////////////////////////////////////////////

//////////// Function to display motor positions relative to start point /////////////
void displayPosition() {

  if (direcX == 1)
  {
    Serial.print("X motor position: ");
    Serial.print(xPosition);
    Serial.print(" mm | ");
  }
  else if(direcX == -1)
  {
    Serial.print("X motor position: ");
    Serial.print(xPosition);
    Serial.print(" mm | ");
  }
  
  if (direcY == 1)
  {
    Serial.print("Y motor position: ");
    Serial.print(yPosition);
    Serial.print(" mm | ");
  }
  else if(direcY == -1)
  {
    Serial.print("Y motor position: ");
    Serial.print(yPosition);
    Serial.print(" mm | ");
  }
  
  if (direcTheta == 1)
  {
    Serial.print("Theta motor position: ");
    Serial.print(thetaPosition);
    Serial.print(" degrees.");
  }
  else if(direcTheta == -1)
  {
    Serial.print("Theta motor position: ");
    Serial.print(thetaPosition);
    Serial.print(" degrees");
  }
 
  Serial.println();
}
///////////////////////////////////////////////////////////////////////////////////////////

//////////// Function to set motors to start position  /////////////
void setToZeroPosition()
{
    if(resetMotor == 1)                    // If the last input is 1 move back all motors to zero position 
    {
        TurnX(xPosition, -1);              // Moving X motor  
        xPosition = 0;                     // Setting xMotor position to zero 
       
        TurnY(-yPosition, 1);
        yPosition = 0;
        
        if(thetaPosition > 0)
        {
          TurnTheta(thetaPosition, -1);
          thetaPosition = 0;
        }
        else if (thetaPosition < 0)
        {
          TurnTheta(-thetaPosition, 1);
          thetaPosition = 0;
        }
        else if(thetaPosition == 0)
        {
          TurnTheta(0,1);
        }
    }
    else if(resetMotor == -1){}           // If the last input is -1 do nothing  
}
////////////////////////////////////////////////////////////////////
// Serial Data For Pump
///////////////////////////////////////////////////////////////////

void recvWithStartEndMarkers() {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;
 
    while (!Serial.available() && newPump == true) {
    //do nothing
    }
        rc = Serial.read();

        if (recvInProgress == true) {
            if (rc != endMarker) {
                receivedCharsP[ndx] = rc;
                ndx++;
                if (ndx >= numCharsP) {
                    ndx = numCharsP - 1;
                }
            }
            else {
                receivedCharsP[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                newPump = true;
            }
        }

        else if (rc == startMarker) {
            recvInProgress = true;
        }
    analogWrite(pump, atoi(receivedCharsP));
}

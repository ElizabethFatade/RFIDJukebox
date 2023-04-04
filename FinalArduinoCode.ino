#include <SPI.h> 
#include <MFRC522.h> 
#include <AccelStepper.h> 
#include <ezButton.h> 
#include <Wire.h>  
#include <Adafruit_PWMServoDriver.h>  


 //Setup values for the RFID Scanner 
#define SS_PIN 10 
#define RST_PIN 9 
MFRC522 mfrc522(SS_PIN, RST_PIN);   // Create MFRC522 instance.

 
//These setup values are for the servo motors on the Claw 
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();  
#define MIN_PULSE_WIDTH       650  
#define MAX_PULSE_WIDTH       2350  
#define FREQUENCY             60  
 
 
//These setup values are for the stepper motor on the Arm 
AccelStepper RailStepper(1,8,9); //This is the stepper motor setup 
ezButton limitSwitch(4); //This is the limit Switch at the bottom of the rail 
ezButton limitSwitch2(6); //This is the limit Switch at the top of the rail
 

const char upButtonPin = 2; //Button to go up 
const char grabButtonPin = 5; //Button to grab the card 
const char downButtonPin = 3; //Button to go down 
 
 
int armLevel = 0;
bool startOver = false; 
 
const int motorSpeed = 400;//Value that makes motor move at a certain speed 
const int distance = 1300; //Value that makes motor move a certain amount 

bool buttonState = false; 

int userMode = -1; //0 - Pushbuttons, 1 - Joysticks, 2 - User control
 
void setup() { 
  // SETUP FOR THE ARM: 
 
 
  Serial.begin(9600);

  Serial.println("Arduino Uploading...\n"); 

  SPI.begin();      // Initiate  SPI bus 
  mfrc522.PCD_Init();   // Initiate MFRC522 
 

  pinMode(upButtonPin, INPUT_PULLUP); //This is how I set up the up,down and grab buttons 
  pinMode(downButtonPin, INPUT_PULLUP); 
  pinMode(grabButtonPin, INPUT_PULLUP); 

 
  //SETUP FOR THE CLAW 
  pwm.begin();  
  pwm.setPWMFreq(FREQUENCY);  // Analog servos run at ~60 Hz updates 
 
   
  // NEXT SET OF COMMANDS ZEROES THE WHOLE SYSTEM 
  setupClaw(); 
  delay(500); 
  setupMotor();  

  //Choose User Control Mode
  userMode = chooseMode(userMode, upButtonPin, downButtonPin, grabButtonPin, buttonState);
  Serial.println(userMode);
} 
 
 
void loop() { 
  // put your main code here, to run repeatedly: 
  
  //Switch case can eb changed to if statements if bothersome
  switch(userMode) {          
    case 0:
      while(userMode == 0) {
        checkPush(upButtonPin, buttonState); 
        checkPush(downButtonPin, buttonState);  
        checkPush(grabButtonPin, buttonState); 
      }
      break;
      
     case 1:
      //Joysticks
      break;

     case 2:    
      //Right now 'V' sent on serial comm will trigger Rock Pi to start recording for 10s aautomatically
      while(userMode == 2) {
          if (Serial.available()) { // If data is available on the serial port
            char voiceCardNumber = Serial.read();
            Serial.print("You have selected card: ");
            Serial.println(voiceCardNumber);

            //Move motor and grab card based on card number
          }
      }
  }
  
} 


int chooseMode(int userMode, const char pinNumber1, const char pinNumber2, const char pinNumber3, bool buttonState) {
  Serial.println("------------------------------------------------");
  Serial.println("Choose how you would like to control the Jukebox");
  Serial.println("------------------------------------------------");
  Serial.println("Left button - Pushbuttons");
  Serial.println("Middle button - Joysticks");
  Serial.println("Right button - Voice control");
  Serial.println("------------------------------------------------");

  while(userMode < 0){
      bool buttonPushed1 = digitalRead(pinNumber1);
      bool buttonPushed2 = digitalRead(pinNumber2);
      bool buttonPushed3 = digitalRead(pinNumber3);      
      
      if ((buttonPushed3 == buttonState) && (pinNumber3 == grabButtonPin)){ 
        Serial.println("Joysticks");  
        userMode = 1;     
        delay(450); 
        while(digitalRead(pinNumber3) == buttonState){ 
        }   
      } 
       
      if ((buttonPushed1 == buttonState) && (pinNumber1 == upButtonPin)){       
        Serial.println("Voice Control");
        userMode = 2;   
        delay(450); 
        while(digitalRead(pinNumber1) == buttonState){ 
        }    
      } 
     
     
      if ((buttonPushed2 == buttonState) && (pinNumber2 == downButtonPin)){      
        Serial.println("Pushbuttons"); 
        userMode = 0;      
        delay(450); 
        while(digitalRead(pinNumber2) == buttonState){ 
        }    
      }  
  }
  return userMode;
 }
 
int pulseWidth(int angle){  
 
 
  int pulse_wide, analog_value;  
  pulse_wide = map(angle,0, 180, MIN_PULSE_WIDTH,MAX_PULSE_WIDTH);// map angle of 0 to 180 to Servo min and Servo max   
 
 
  analog_value = int(float(pulse_wide) / 1000000 * FREQUENCY * 4096);  
  //Serial.println(analog_value);  
  return analog_value;   
 
 
}  
 
 
void setupMotor(){ //This function sends the arm all the way down 
 
 
  RailStepper.setMaxSpeed(500);  
  RailStepper.setSpeed(-motorSpeed); 
  limitSwitch.setDebounceTime(50); 
   
  bool limitState1 = false; 
  bool limitState2 = true; 
    
  while(limitState1 != true){ 
    RailStepper.runSpeed(); 
    limitSwitch.loop(); 
    if(limitSwitch.isPressed()){  
      RailStepper.stop(); 
      limitState1 = true;  
      break;     
    }     
  } 
  delay(1000); 
  RailStepper.setSpeed(motorSpeed); 
   
  while(limitState2 != false){ 
    RailStepper.runSpeed();  
    limitSwitch.loop(); 
    if(limitSwitch.isReleased()) { 
      limitState2 = false; 
      break; 
    }   
  } 
  
} 
 
 
void setupClaw(){ 
   // Shoulder twist  
   pwm.setPWM(12, 0, pulseWidth(145)); // zero is 90, 120 is to grab and take the card
   delay(600);   
 
 
   // Shoulder up/down  
   pwm.setPWM(13, 0, pulseWidth(70)); // zero is 50, 120 is to grab the card
   delay(600);  
 
 
   // Elbow  
   pwm.setPWM(14, 0, pulseWidth(70)); // zero is 60, 5 is to grab the card 
   delay(600);  
 
 
   // Claw  
   pwm.setPWM(15, 0, pulseWidth(40)); // Open is 40, 55 is to grab the card  
   delay(600);  
 
 
} 
 
 
void checkPush(const char pinNumber, bool buttonState) { //This function determines which button is pressed 
   
  bool buttonPushed = digitalRead(pinNumber); 
  
  
  if ((buttonPushed == buttonState) && (pinNumber == grabButtonPin)){ 
    Serial.println("grab button"); 
    
    
    grabCard(armLevel); 
    armLevel = armCounter(pinNumber, armLevel, true);      
    delay(450); 
    while(digitalRead(pinNumber) == buttonState){ 
    }
     
  } 
   
  if ((buttonPushed == buttonState) && (pinNumber == upButtonPin)){ 
 
    armLevel = armCounter(pinNumber, armLevel, false); 
    Serial.print("Going up to level ");
    Serial.println(armLevel); 
    moveMotor(distance);     
    delay(450); 
    while(digitalRead(pinNumber) == buttonState){ 
    }    
  } 
 
 
  if ((buttonPushed == buttonState) && (pinNumber == downButtonPin)){ 
     
    armLevel = armCounter(pinNumber, armLevel, false); 
    Serial.print("Going down to level ");
    Serial.println(armLevel);     
    moveMotor(-distance);   
    delay(450); 
    while(digitalRead(pinNumber) == buttonState){ 
    }    
  }    
} 

 
 
bool returnCheckPush (const char pinNumber, bool buttonState, int armLevel){ 
   
  bool buttonPushed = digitalRead(pinNumber); 
   
  if ((buttonPushed == buttonState) && (pinNumber == grabButtonPin)){ 
    returnCard(armLevel); 
    return false;   
    delay(450); 
    while(digitalRead(pinNumber) == buttonState){ 
    } 
  } 
  return true; 
} 

int armCounter(const char pinNumber, int armLevel, bool startOver){

  if((pinNumber == upButtonPin) && (startOver == false)){
    armLevel = armLevel+1;
  }
  if((pinNumber == downButtonPin) && (startOver == false)){
    armLevel = armLevel-1;
    if(armLevel == -1){
      armLevel = 0;
    }
  }
  if((pinNumber == grabButtonPin) && (startOver == true)){
    armLevel = 0;
  }

  return armLevel;
  
}
 
 
void moveMotor(int distance){ //Depending on which button is pressed, this function moves the arm up or down 
  RailStepper.setCurrentPosition(0); 
  if(distance == abs(distance)){ 
    RailStepper.setSpeed(motorSpeed); 
  }else{ 
    RailStepper.setSpeed(-motorSpeed); 
  }   
   
  while(RailStepper.currentPosition() != distance){ 
    limitSwitch.loop();
    limitSwitch2.loop(); 
    RailStepper.runSpeed(); 
    RailStepper.currentPosition(); 
    //Serial.println(RailStepper.currentPosition()); 
    if(limitSwitch.isPressed()){ 
      RailStepper.stop(); 
      delay(1000); 
      resetMotor(distance); 
      break;      
    }
    if(limitSwitch2.isPressed()){
      RailStepper.stop();
      delay(1000);
      resetMotor(distance);
      break;  
    }
  } 
   
} 
 
 
void grabCard(int armLevel) { 
 
 
   bool clawState = true; 
   //CLAW GRABS THE CARD

   // Shoulder up/down  
   pwm.setPWM(13, 0, pulseWidth(80)); // zero is 50, 80 is to grab the card
//   moveServo(13, 90);
   delay(600);
    
   // Elbow  
   pwm.setPWM(14, 0, pulseWidth(5)); // Bend in towards card 
//   moveServo(14, 25);
   delay(600);  
 
 
   // Claw  
   pwm.setPWM(15, 0, pulseWidth(65)); // Close
//   moveServo(15, 65); 
   delay(700);  
 
 
   //CLAW TAKES THE CARD TOWARDS SCANNER
   //Shoulder 
   pwm.setPWM(12, 0, pulseWidth(125)); //Bend out 
//   moveServo(12, 125);
   delay(900);

   // Shoulder up/down  
   pwm.setPWM(13, 0, pulseWidth(5)); // zero is 50, 120 is to grab the card
//   moveServo(13, 0);
   delay(600); 

    // Elbow  
   pwm.setPWM(14, 0, pulseWidth(30)); // Bend  
//   moveServo(14, 30);
   delay(1000);
    
   setupMotor(); 
   delay(750); 
 
 
   pwm.setPWM(12, 0, pulseWidth(150)); //Shoulder tilt down 
//   moveServo(12, 150);

   delay(1000);
   Serial.println("Loading music");
   readCard();
    
   while(clawState != false){    
    clawState = returnCheckPush (grabButtonPin, buttonState, armLevel);
     
   } 

   
} 
 
 
void returnCard(int armLevel){//This is a temporary function of what the arm will do once its done playing music 
  Serial.println("Stopping music");

  //This is where I want the code to read the serial monitor 

  //I want to name the int from the serial monitor count

  delay(200);
  moveMotor(armLevel*distance);
  delay(1000);
   
  //Shoulder
  pwm.setPWM(12, 0, pulseWidth(125)); //Shoulder tilts back up 
  delay(700);

   //Elbow 
   pwm.setPWM(14, 0, pulseWidth(5)); // Bend  
   delay(700);

  // Shoulder up/down  
   pwm.setPWM(13, 0, pulseWidth(80)); // zero is 50, 90 is to grab the card
   delay(700);

   

   //Shoulder
  pwm.setPWM(12, 0, pulseWidth(145)); //Shoulder tilts back down to leave card 
  delay(700);

  // Claw  
   pwm.setPWM(15, 0, pulseWidth(40)); // Open 
   delay(600);
  
   //Elbow 
   pwm.setPWM(14, 0, pulseWidth(90)); // Bend  
   delay(600);


   setupClaw();
   delay(200);
   setupMotor();
  
   
} 
 
 
void resetMotor(int distance){ //if the limit switch is pressed while moveMotor is running, this resets the arm to go back into the rail 
  bool limitState = true; 
   
  if(distance == abs(distance)){ 
    RailStepper.setSpeed(-motorSpeed); 
  }else{ 
    RailStepper.setSpeed(motorSpeed); 
  } 
  
  while(limitState != false){ 
    RailStepper.runSpeed();  
    limitSwitch.loop();
    limitSwitch2.loop(); 
    if(limitSwitch.isReleased()) { 
      limitState = false; 
      break; 
    }
    if(limitSwitch2.isReleased()){
      limitState = false;
      break;   
    }
  } 
    
}

void readCard() { 

  // Look for new cards 
  if ( ! mfrc522.PICC_IsNewCardPresent())  
  { 
    
    //break;
     
  } 
  
  // Select one of the cards 
  if ( ! mfrc522.PICC_ReadCardSerial())  
  {
    //break;
     
  } 
  
  //Show UID on serial monitor 
  
  Serial.print("UID tag :"); 
  delay(800);
  String content= ""; 
  byte letter; 
  for (byte i = 0; i < mfrc522.uid.size; i++)  
  { 
     Serial.print(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " "); 
     Serial.print(mfrc522.uid.uidByte[i], HEX); 
     content.concat(String(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " ")); 
     content.concat(String(mfrc522.uid.uidByte[i], HEX)); 
  } 
  
  delay(800);
  Serial.println(" ");  
} 

void moveServo(int pinNum, int dest) {

  int i = pwm.getPWM(pinNum);
  if(i < dest) {
    while (i < dest) { //ex 30 -> 90
      pwm.setPWM(pinNum, 0, pulseWidth(i));
      i++;
      delay(10);
    }
  }
  else {
    while (i > dest) { //eg 90 -> 30
      pwm.setPWM(pinNum, 0, pulseWidth(i));
      i--;
      delay(10);
    }
  }
}

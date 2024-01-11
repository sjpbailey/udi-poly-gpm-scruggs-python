int sensorInterrupt = 0;  // interrupt 0

const int sensorPin       = 2; //Digital Pin 2
//int highLevel=6;// initialize pin 13 for pool level High
//int lowLevel=7;// initialize pin 12 for pool level Low
//int valHigh;// define val  for pool level High
//int valLow;// define val  for pool level Low
int ledpin=13;// initialize pin 13
int inpin=6;// initialize pin 6
int inpin2=7;// initialize pin 7

int val;// define val
int val2;// define val
int solenoidValve = 5; // Digital pin 5
unsigned int SetPoint = 400; //400 milileter

/*The hall-effect flow sensor outputs pulses per second per litre/minute of flow.*/
float calibrationFactor = .2; //For 2" .2Note: F=(0.2*Q)±2% for this flow sensor, Q=L/Min, and F is pulse freq

volatile byte pulseCount =0;  

float flowRate = 0.0;

unsigned int flowMilliLitres =0;
unsigned int flowGPM =0;

unsigned long totalMilliLitres =0; 
unsigned long totalGPM =0;
unsigned long oldTime =0;

const int pressureInput = A0; //select the analog input pin for the pressure transducer
const int pressureZero = 102.4; //analog reading of pressure transducer at 0psi
const int pressureMax = 921.6; //analog reading of pressure transducer at 100psi
const int pressuretransducermaxPSI = 100; //psi value of transducer being used

float pressureValue = 0; //variable to store the value coming from the pressure transducer

void setup()
{

  // Initialize a serial connection for reporting values to the host
  Serial.begin(9600);

  pinMode(solenoidValve , OUTPUT);
  digitalWrite(solenoidValve, HIGH);

  pinMode(sensorPin, INPUT);
  digitalWrite(sensorPin, HIGH);

  //pinMode(highLevel,INPUT); // set LED pin as “input”
  //pinMode(lowLevel,INPUT); // set button pin as “input”
  pinMode(ledpin,OUTPUT);// set LED pin as “output”
  pinMode(inpin,INPUT);// set button pin as “input”
  pinMode(inpin2,INPUT);// set button pin as “input”
  
  /*The Hall-effect sensor is connected to pin 2 which uses interrupt 0. Configured to trigger on a FALLING state change (transition from HIGH
   (state to LOW state)*/
  attachInterrupt(sensorInterrupt, pulseCounter, FALLING); //you can use Rising or Falling

  //pinMode(3, OUTPUT);  //assign pin 2 as output;
  //digitalWrite(3,digitalRead(sensorPin))  // to retransmit pin2 ;
  //attachInterrupt(sensorInterrupt, pulseCounter, FALLING); //you can use Rising or Falling
}

void loop()
{

  if((millis() - oldTime) > 3000)    // Only process counters once per second
  { 
    // Disable the interrupt while calculating flow rate and sending the value to the host
    detachInterrupt(sensorInterrupt);

    // Because this loop may not complete in exactly 1 second intervals we calculate the number of milliseconds that have passed since the last execution and use that to scale the output. We also apply the calibrationFactor to scale the output based on the number of pulses per second per units of measure (litres/minute in this case) coming from the sensor.
    flowRate = ((1000.0 / (millis() - oldTime)) * pulseCount) / calibrationFactor;

    // Note the time this processing pass was executed. Note that because we've
    // disabled interrupts the millis() function won't actually be incrementing right
    // at this point, but it will still return the value it was set to just before
    // interrupts went away.
    oldTime = millis();

    // Divide the flow rate in litres/minute by 60 to determine how many litres have
    // passed through the sensor in this 1 second interval, then multiply by 1000 to
    // convert to millilitres.
    flowMilliLitres = (flowRate / 60) * 1000;
    flowGPM = flowMilliLitres * .016;
    // Add the millilitres passed in this second to the cumulative total
    totalMilliLitres += flowMilliLitres;
    totalGPM = totalMilliLitres *.016 / 60;

    unsigned int frac;
    //int valuehigh;
    //int valuelow;
    //valuelow=digitalRead(lowLevel);// read the level value of pin 12 and assign if to val   
    //valuehigh=digitalRead(highLevel);// read the level value of pin 13 and assign if to val
    val=digitalRead(inpin);// read the level value of pin 7 and assign if to val
    val2=digitalRead(inpin2);// read the level value of pin 7 and assign if to val
    
    pressureValue = analogRead(pressureInput); //reads value from input pin and assigns to variable
    pressureValue = ((pressureValue-pressureZero)*pressuretransducermaxPSI)/(pressureMax-pressureZero); //conversion equation to convert analog reading to psi

    Serial.print(flowGPM, DEC);  // Print the integer part of the variabl
    Serial.print(" , "); // Print the cumulative total of GPM flowed since starting
    Serial.print(totalGPM,DEC);
    Serial.print(" , ");
    Serial.print(pressureValue, 1);
    Serial.print(" , ");
    //Serial.print(valuehigh);
    //Serial.print(" , ");
    //Serial.println(valuelow);
    Serial.print(val); // print the data from the sensor
    Serial.print(" , ");
    Serial.println(val2); // print the data from the sensor
    if (totalMilliLitres > 40)
    {
      SetSolinoidValve();
    }

    // Reset the pulse counter so we can start incrementing again
    pulseCount = 0;

    // Enable the interrupt again now that we've finished sending output
    attachInterrupt(sensorInterrupt, pulseCounter, FALLING);
  }
}

//Insterrupt Service Routine

void pulseCounter()
{
  // Increment the pulse counter
  pulseCount++;
}

void SetSolinoidValve()
{
  digitalWrite(solenoidValve, LOW);
}

// Print the flow rate for this second in litres / minute
//Serial.print("Flow rate: ");
//Serial.print(flowGPM, DEC);  // Print the integer part of the variable
//Serial.print("GPM");
//Serial.print("\t");           

// Print the cumulative total of litres flowed since starting
//Serial.print("Output Liquid Quantity: ");        
//Serial.print(totalGPM,DEC);
//Serial.println("Gallons"); 
//Serial.print("\t");     

//if (totalMilliLitres > 40)
//{
//  SetSolinoidValve();
//}

// Reset the pulse counter so we can start incrementing again
//pulseCount = 0;

// Enable the interrupt again now that we've finished sending output
//attachInterrupt(sensorInterrupt, pulseCounter, FALLING);
//}
//}

//Insterrupt Service Routine

//void pulseCounter()
//{
// Increment the pulse counter
//pulseCount++;
//}

//void SetSolinoidValve()
//{
// digitalWrite(solenoidValve, LOW);
//}

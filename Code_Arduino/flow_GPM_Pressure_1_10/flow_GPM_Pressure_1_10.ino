
// This section for Temperature Sensor
int sensorInterrupt = 0;  // interrupt 0
#include <OneWire.h>
#include <DallasTemperature.h>

float tempCelsius;    // temperature in Celsius
float tempFahrenheit; // temperature in Fahrenheit
unsigned long int avgValue;  //Store the average value of the sensor feedback
float b;
int buf[10],temp;
//End Section for Temperature Sensor





const int sensorPin = 2; //Digital Pin 2 Flow Meter
int solenoidValve = 5; // Digital pin 5 Solenoid Valve
int inpin = 6;// initialize pin 6 Water Level
int inpin2 = 7;// initialize pin 7 Water Level 
const int tempSensor_Pin = 8; // Arduino pin connected to DS18B20 Temperature sensor's DQ pin
OneWire oneWire(tempSensor_Pin);         // setup a oneWire instance for Temperature
DallasTemperature tempSensor(&oneWire); // pass oneWire to DallasTemperature library
int ledpin = 13;// initialize pin 13 solenoid
int val1; // define val1 Water Level
int val2; // define val2 Water Level


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
float     pressureValue = 0; //variable to store the value coming from the pressure transducer
const int PH_Input = A2; //select the analog input pin for the PH Input

//This section for ORP
#define VOLTAGE 5.00    //system voltage
#define OFFSET 0        //zero drift voltage
#define LEDORP 11         //operating instructions

double orpValue;

#define ArrayLenth  40    //times of collection
#define orpPin A1          //orp meter output,connect to Arduino controller ADC pin

int orpArray[ArrayLenth];
int orpArrayIndex=0;

double avergearray(int* arr, int number){
  int i;
  int max,min;
  double avg;
  long amount=0;
  if(number<=0){
    printf("Error number for the array to avraging!/n");
    return 0;
  }
  if(number<5){   //less than 5, calculated directly statistics
    for(i=0;i<number;i++){
      amount+=arr[i];
    }
    avg = amount/number;
    return avg;
  }else{
    if(arr[0]<arr[1]){
      min = arr[0];max=arr[1];
    }
    else{
      min=arr[1];max=arr[0];
    }
    for(i=2;i<number;i++){
      if(arr[i]<min){
        amount+=min;        //arr<min
        min=arr[i];
      }else {
        if(arr[i]>max){
          amount+=max;    //arr>max
          max=arr[i];
        }else{
          amount+=arr[i]; //min<=arr<=max
        }
      }//if
    }//for
    avg = (double)amount/(number-2);
  }//if
  return avg;
}
 // End of ORP section

void setup() {

  // Initialize a serial connection for reporting values to the host
  Serial.begin(9600);
  pinMode(LEDORP,OUTPUT);
  pinMode(12,OUTPUT);  //added for PH led
  pinMode(solenoidValve , OUTPUT);
  digitalWrite(solenoidValve, HIGH);

  pinMode(sensorPin, INPUT);
  digitalWrite(sensorPin, HIGH);
  
  pinMode(ledpin,OUTPUT);// set LED pin as “output”
  pinMode(inpin,INPUT);// set button level pin as “input”
  pinMode(inpin2,INPUT);// set button level pin as “input”
  pinMode(LEDORP,OUTPUT);
  //*The Hall-effect sensor is connected to pin 2 which uses interrupt 0. Configured to trigger on a FALLING state change (transition from HIGH
   //(state to LOW state)*/
  attachInterrupt(sensorInterrupt, pulseCounter, FALLING); //you can use Rising or Falling
 
}

void loop()  // void loo[() and void loop(void) are the same
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
    //valuelow=digitalRead(lowLevel);// read the level value of pin 12 and assign if to val1   
    //valuehigh=digitalRead(highLevel);// read the level value of pin 13 and assign if to val1
    val1=digitalRead(inpin);// read the level value of pin 6 Water Level and assign if to val1
    val2=digitalRead(inpin2);// read the level value of pin 7 Water Level and assign if to val2
    
    pressureValue = analogRead(pressureInput); //reads value from input pin AO and assigns to variable
    pressureValue = ((pressureValue-pressureZero)*pressuretransducermaxPSI)/(pressureMax-pressureZero); //conversion equation to convert analog reading to psi

//Adding PH to sketch in this section

for(int i=0;i<10;i++)       //Get 10 sample value from the sensor for smooth the value
 { 
   buf[i]=analogRead(PH_Input);
    delay(10);
  }
 for(int i=0;i<9;i++)        //sort the analog from small to large
 {
  for(int j=i+1;j<10;j++)
  {
    if(buf[i]>buf[j])
   {
        temp=buf[i];
        buf[i]=buf[j];
       buf[j]=temp;
     }
    }
  }
  avgValue=0;
  for(int i=2;i<8;i++)                      //take the average value of 6 center sample
   avgValue+=buf[i];
  float phValue=(float)avgValue*5.0/1024/6; //convert the analog into millivolt
  phValue=3.5*phValue;                      //convert the millivolt into pH value

//Ending adding PH 
//Temperature Sensor Starts here
tempSensor.requestTemperatures();             // send the command to get temperatures
  tempCelsius = tempSensor.getTempCByIndex(0);  // read temperature in Celsius
  tempFahrenheit = tempCelsius * 9 / 5 + 32; // convert Celsius to Fahrenheit
//Temperature sensor ends here. Note, not printing celsius
//ORP starts here.
static unsigned long orpTimer=millis();   //analog sampling interval
  static unsigned long printTime=millis();
  if(millis() >= orpTimer)
  {
    orpTimer=millis()+20;
    orpArray[orpArrayIndex++]=analogRead(orpPin);    //read an analog value every 20ms
    if (orpArrayIndex==ArrayLenth) {
      orpArrayIndex=0;
    }   
    orpValue=((30*(double)VOLTAGE*1000)-(75*avergearray(orpArray, ArrayLenth)*VOLTAGE*1000/1024))/75-OFFSET;   //convert the analog value to orp according the circuit
  }
//ORP ends here


    Serial.print(flowGPM, DEC);  // Print the integer part of the variabl
    Serial.print(" , "); // Print the cumulative total of GPM flowed since starting
    Serial.print(totalGPM,DEC);
    Serial.print(" , ");
    Serial.print(pressureValue, 1);
    Serial.print(" , ");
    Serial.print(val1); // print the data from the Low Level sensor
    Serial.print(" , ");
    Serial.print(val2); // print the data from the High Level sensor
    Serial.print(" , ");
    Serial.print(phValue,2);
    Serial.print(" , ");
    Serial.print((int)orpValue);
    Serial.print(" , ");
    Serial.println(tempFahrenheit); // print the temperature in Fahrenheit
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

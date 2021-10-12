/*
    Code description: Code designed for receiving specific UDP packets
    and returning data. Used for controlling 4 PWM signals.

    Created by: Keenan Robinson
    Date modified: 12/10/2021
    
 */


#include <EthernetENC.h>
#include <EthernetUdp.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

#define UDP_TX_PACKET_MAX_SIZE 256 //Needed for EthernetENC

// Enter a MAC address and IP address for your controller below.
// The IP address will be dependent on your local network:
byte mac[] = {
  0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED
};
IPAddress ip(192, 168, 0, 132); 

unsigned int localPort = 5000;      // local port to listen on

// buffers for receiving and sending data
char packetBuffer[UDP_TX_PACKET_MAX_SIZE];  // buffer to hold incoming packet,
//char replyBuffer[] = "acknowledged";        // a string to send back
//char replyBuffer1[] = "acknowledged";        // a string to send back
char reply[50];

//Arduino PWM pins and values
#define pin0 3
#define pin1 5
#define pin2 6
#define pin3 9

int dutyCycle0 = 0;
int dutyCycle1 = 0;
int dutyCycle2 = 0;
int dutyCycle3 = 0;

// An EthernetUDP instance to let us send and receive packets over UDP
EthernetUDP Udp;

void setup() {
    // You can use Ethernet.init(pin) to configure the CS pin
    //Ethernet.init(10);  // Most Arduino shields
    //Ethernet.init(5);   // MKR ETH shield
    //Ethernet.init(0);   // Teensy 2.0
    //Ethernet.init(20);  // Teensy++ 2.0
    //Ethernet.init(15);  // ESP8266 with Adafruit Featherwing Ethernet
    //Ethernet.init(33);  // ESP32 with Adafruit Featherwing Ethernet

    //Set PWM pins
    pinMode(pin0, OUTPUT);
    pinMode(pin1, OUTPUT);
    pinMode(pin2, OUTPUT);
    pinMode(pin3, OUTPUT);
    analogWrite(pin0, 0);
    analogWrite(pin1, 0);
    analogWrite(pin2, 0);
    analogWrite(pin3, 0);
    dutyCycle0 = 0;
    dutyCycle1 = 0;
    dutyCycle2 = 0;
    dutyCycle3 = 0;

    // start the Ethernet
    Ethernet.begin(mac, ip);

    // Open serial communications and wait for port to open:
    Serial.begin(9600);
    while (!Serial) {
        ; // wait for serial port to connect. Needed for native USB port only
    }

    // Check for Ethernet hardware present
    if (Ethernet.hardwareStatus() == EthernetNoHardware) {
        Serial.println("Ethernet shield was not found.  Sorry, can't run without hardware. :(");
        while (true) {
            delay(1); // do nothing, no point running without Ethernet hardware
        }
    }
    if (Ethernet.linkStatus() == LinkOFF) {
        delay(500);
        if (Ethernet.linkStatus() == LinkOFF) {
            Serial.println("Ethernet cable is not connected.");
        }
    }
    // start UDP
    Udp.begin(localPort);
}

void loop() {
  // if there's data available, read a packet
    int packetSize = Udp.parsePacket();
    if (packetSize) {
        Serial.print("Received packet of size ");
        Serial.println(packetSize);
        Serial.print("From ");
        IPAddress remote = Udp.remoteIP();
        for (int i=0; i < 4; i++) {
            Serial.print(remote[i], DEC);
            if (i < 3) {
                Serial.print(".");
            }
        }
        Serial.print(", port ");
        Serial.println(Udp.remotePort());

        // read the packet into packetBufffer
        Udp.read(packetBuffer, UDP_TX_PACKET_MAX_SIZE);
        Serial.println("Contents:");
        Serial.println(packetBuffer);
        //UDP packet handling:
        //uint8_t pwmPin;
        //uint8_t dutyCycle;
        if(strcmp(packetBuffer, "!PING") == 0) { //if strings are equal
            Serial.println("!PING acknowledged");
            memset(reply, '\0', sizeof(reply)); //Set null-terminating chars in all positions of the char array
            strcpy(reply, "acknowledged");
            Serial.println(reply);
        }
        else if(strcmp(packetBuffer, "!PING_test") == 0) { //if strings are equal
            Serial.println("!PING acknowledged");
            memset(reply, '\0', sizeof(reply)); //Set null-terminating chars in all positions of the char array
            strcpy(reply, "acknowledged_test");
            Serial.println(reply);
        }
        else if(strcmp(packetBuffer, "!REQUEST_CONFIG") == 0) { //if strings are equal
            Serial.println("!REQUEST_CONFIG acknowledged");
            memset(reply, '\0', sizeof(reply)); //Set null-terminating chars in all positions of the char array
            char* configs;
            configs= printCurrentConfig(dutyCycle0, dutyCycle1, dutyCycle2, dutyCycle3);
            Serial.print("configs");
            Serial.println(configs);
            strcpy(reply, configs);
            free(configs);
            Serial.println(reply);
        }
        else {
            Serial.println("Update PWM request");
            //memset(replyBuffer, '\0', sizeof(replyBuffer)); //Set null-terminating chars in all positions of the char array
            //strcpy(replyBuffer, "Done nothing.");
            //extractString(packetBuffer);
            updatePWM(packetBuffer, &dutyCycle0, &dutyCycle1, &dutyCycle2, &dutyCycle3);
            Serial.println(dutyCycle0);
            Serial.println(dutyCycle1);
            Serial.println(dutyCycle2);
            Serial.println(dutyCycle3);
        }
        
        for(int i=0; i<UDP_TX_PACKET_MAX_SIZE; i++) packetBuffer[i] = 0; //Clears packetBuffer 
    
        // send a reply to the IP address and port that sent us the packet we received
        Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
        Udp.write(reply);
        Udp.endPacket();
        //for(int i=0; i<50; i++) reply[i] = 0; //Clears replyBuffer
    }
    delay(10);
}

char * printCurrentConfig(uint8_t dutyCycle0, uint8_t dutyCycle1, uint8_t dutyCycle2, uint8_t dutyCycle3) {
    //When a read config command is sent to the arduino
    Serial.println(dutyCycle0);
    Serial.println(dutyCycle1);
    Serial.println(dutyCycle2);
    Serial.println(dutyCycle3);
    char *configString = malloc (sizeof (char) * 50);
    //char configString[50];
    memset(configString, '\0', sizeof(configString)); //Set null-terminating chars in all positions of the char array
    //Pointers to values of the pins stored as strings
    char p_pin0[2];
    char p_pin1[2];
    char p_pin2[2];
    char p_pin3[2];
    
    sprintf(p_pin0, "%d", pin0);
    sprintf(p_pin1, "%d", pin1);
    sprintf(p_pin2, "%d", pin2);
    sprintf(p_pin3, "%d", pin3);
    
    //Pointers to values of the duty cycles converted to strings
    char p_dutyCycle0[4];
    char p_dutyCycle1[4];
    char p_dutyCycle2[4];
    char p_dutyCycle3[4];
    
    sprintf(p_dutyCycle0, "%d", dutyCycle0);
    sprintf(p_dutyCycle1, "%d", dutyCycle1);
    sprintf(p_dutyCycle2, "%d", dutyCycle2);
    sprintf(p_dutyCycle3, "%d", dutyCycle3);

    //String formatting
    strcat(configString, p_pin0);
    strcat(configString, "_");
    strcat(configString, p_dutyCycle0);
    strcat(configString, "|");
    strcat(configString, p_pin1);
    strcat(configString, "_");
    strcat(configString, p_dutyCycle1);
    strcat(configString, "|");
    strcat(configString, p_pin2);
    strcat(configString, "_");
    strcat(configString, p_dutyCycle2);
    strcat(configString, "|");
    strcat(configString, p_pin3);
    strcat(configString, "_");
    strcat(configString, p_dutyCycle3);
    
    return configString;
}

////Server functions////
void updatePWM(char arr[256], int *dutyCycle0, int *dutyCycle1, int *dutyCycle2, int *dutyCycle3 ) {
    char *idPosition; //Used to locate the substring "_"
    char *dutyCPos;

    idPosition = strstr(arr, "_"); //Stores the substring
    Serial.println(arr);
    if(idPosition != NULL) {
        //Found:
        //Serial.print("Found _ at index: ");
        //Serial.println(idPosition-arr); //This is the index of the found substring
        uint8_t pinNo = (int)strtol(arr, &dutyCPos, 10); //Extract pin value
        uint8_t dutyCycle = atoi(dutyCPos+1); //Extract the duty cycle value
        Serial.println(pinNo);
        Serial.println(dutyCycle);
        //Update PWM values:
        uint8_t dutyVal = map(dutyCycle, 0, 100, 0, 255);
        if(pinNo == pin0) {
            analogWrite(pinNo, dutyVal);
            *dutyCycle0 = dutyCycle;
        }
        else if(pinNo == pin1) {
            analogWrite(pinNo, dutyVal);
            *dutyCycle1 = dutyCycle;
        }
        else if(pinNo == pin2) {
            analogWrite(pinNo, dutyVal);
            *dutyCycle2 = dutyCycle;
        }
        else if(pinNo == pin3) {
            analogWrite(pinNo, dutyVal);
            *dutyCycle3 = dutyCycle;
        }
        else Serial.println("Error in updating PWM"); //you need to notify the user the wrong config has been setup
    }
    else {
        //Not found:
        Serial.println("Message does not follow the specified format.");
    }
}

/* Deprecated:
 * void updatePWM(uint8_t pinNo, uint8_t dutyCycle) {
  Serial.print("updatePWM called!\n");
  uint8_t val = map(dutyCycle, 0, 100, 0, 255);
  if(pinNo == pin0 || pinNo == pin1 || pinNo == pin2 || pinNo == pin3) analogWrite(pinNo, val);
  else Serial.println("Error in updating PWM"); //you need to notify the user the wrong config has been setup
}

void extractString(char arr[256]) {
    char *idPosition; //Used to locate the substring "_"
    char *test;

    idPosition = strstr(arr,"_"); //Stores the substring
    Serial.println(arr);
    if(idPosition != NULL) {
        //Found:
        //Serial.print("Found _ at index: ");
        //Serial.println(idPosition-arr); //This is the index of the found substring
        uint8_t pinVal = (int)strtol(arr, &test, 10); //Extract pin value
        uint8_t dutyC = atoi(test+1); //Extract the duty cycle value
        //Serial.println(pinVal);
        //Serial.println(atoi(test+1));
        updatePWM(pinVal, dutyC);
    }
    else {
        //Not found:
        Serial.println("Nothing");
    }
}*/

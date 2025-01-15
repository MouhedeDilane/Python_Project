#include <Ethernet.h>     //Load Ethernet Library
#include <EthernetUdp.h>  //Load the Udp Library
#include <SPI.h>          //Load SPI Library


byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xEE };  //Assign mac address
IPAddress ip(192, 168, 0, 101);                       //Assign the IP Adress
unsigned int localPort = 5000;                        // Assign a port to talk over
char packetBuffer[UDP_TX_PACKET_MAX_SIZE];            //dimensian a char array to hold our data packet
String datReq;                                        //String for our data
int packetSize;                                       //Size of the packet
EthernetUDP Udp;                                      // Create a UDP Object


unsigned long t;
const byte header1 = 0xFF;
const byte header2 = 0xFF;
byte nL, nR, t1, t2, t3, t4;


void setup() {

  Serial.begin(9600);       //Initialize Serial Port
  Ethernet.begin(mac, ip);  //Inialize the Ethernet
  Udp.begin(localPort);     //Initialize Udp
  delay(1500);              //delay
}

void loop() {
  
  packetSize =Udp.parsePacket(); //Reads the packet size
  int n = 0;  // numbers the arrays
  
  if(packetSize>0) { //if packetSize is >0, that means someone has sent a request
    unsigned long t0 = millis();
    while(1) {

      // array ID
      nL = (n & 0xFF00) >> 8;
      nR = n & 0x00FF;

      // time
      t = millis();
      t1 = (t >> 24) & 0xFF;
      t2 = (t >> 16) & 0xFF;
      t3 = (t >> 8) & 0xFF;
      t4 = t & 0xFF;

      // pressure sensors
      int P1 = analogRead(A0);  
      int P2 = analogRead(A1);
      int P3 = analogRead(A2);
      int P4 = analogRead(A3);
      int P5 = analogRead(A4);
      int P6 = analogRead(A5);
      int P7 = analogRead(A6);
      int P8 = analogRead(A7);
      int P9 = analogRead(A8);
      int P10 = analogRead(A9);
      byte P1L = (P1 & 0xFF00) >> 8;
      byte P1R = P1 & 0x00FF;
      byte P2L = (P2 & 0xFF00) >> 8;
      byte P2R = P2 & 0x00FF;
      byte P3L = (P3 & 0xFF00) >> 8;
      byte P3R = P3 & 0x00FF;
      byte P4L = (P4 & 0xFF00) >> 8;
      byte P4R = P4 & 0x00FF;
      byte P5L = (P5 & 0xFF00) >> 8;
      byte P5R = P5 & 0x00FF;
      byte P6L = (P6 & 0xFF00) >> 8;
      byte P6R = P6 & 0x00FF;
      byte P7L = (P7 & 0xFF00) >> 8;
      byte P7R = P7 & 0x00FF;
      byte P8L = (P8 & 0xFF00) >> 8;
      byte P8R = P8 & 0x00FF;
      byte P9L = (P9 & 0xFF00) >> 8;
      byte P9R = P9 & 0x00FF;

      // temperature sensors
      int T1 = 100*sin(t);
      int T2 = 100*sin(t + 1);
      int T3 = 100*sin(t + 2);
      int T4 = 100*sin(t + 3);
      int T5 = 100*sin(t + 4);
      byte T1L = (T1 & 0xFF00) >> 8;
      byte T1R = T1 & 0x00FF;
      byte T2L = (T2 & 0xFF00) >> 8;
      byte T2R = T2 & 0x00FF;
      byte T3L = (T3 & 0xFF00) >> 8;
      byte T3R = T3 & 0x00FF;
      byte T4L = (T4 & 0xFF00) >> 8;
      byte T4R = T4 & 0x00FF;
      byte T5L = (T5 & 0xFF00) >> 8;
      byte T5R = T5 & 0x00FF;

      // force sensor
      int F1 = 50*sin(t);
      byte F1L = (F1 & 0xFF00) >> 8;
      byte F1R = F1 & 0x00FF;

      // flow sensors
      int FL1 = 100*sin(t);
      int FL2 = 100*sin(t + 1);
      int FL3 = 100*sin(t + 2);
      byte FL1L = (FL1 & 0xFF00) >> 8;
      byte FL1R = FL1 & 0x00FF;
      byte FL2L = (FL2 & 0xFF00) >> 8;
      byte FL2R = FL2 & 0x00FF;
      byte FL3L = (FL3 & 0xFF00) >> 8;
      byte FL3R = FL3 & 0x00FF;

      byte frame[44] = {
        header1, header2,
        nL, nR,
        t1,t2,t3,t4,
        P1L, P1R,
        P2L, P2R,
        P3L, P3R,
        P4L, P4R,
        P5L, P5R,
        P6L, P6R,
        P7L, P7R,
        P8L, P8R,
        P9L, P9R,
        T1L, T1R,
        T2L, T2R,
        T3L, T3R,
        T4L, T4R,
        T5L, T5R,
        FL1L, FL1R,
        FL2L, FL2R,
        FL3L, FL3R
      };
      Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());  //Initialize packet send
      Udp.write(frame, 44);                               //Send the Pressure data
      Udp.endPacket();                                    //End the packet

      n++;
      delay(1000);
      if (millis() - t0 >= 100000) {
        Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());  //Initialize packet send
        Udp.print("Exit");                                  //Send the Pressure data
        Udp.endPacket();
        break;
      }
    }      
  }
  memset(packetBuffer, 0, UDP_TX_PACKET_MAX_SIZE); //clear out the packetBuffer array
}
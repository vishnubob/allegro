// Defines for use with Arduino functions
#define clockpin   13 // CL
#define enablepin  10 // BL
#define latchpin    9 // XL
#define datapin    11 // SI
 
// Defines for direct port access
#define CLKPORT PORTB
#define ENAPORT PORTB
#define LATPORT PORTB
#define DATPORT PORTB
#define CLKPIN  5
#define ENAPIN  2
#define LATPIN  1
#define DATPIN  3
 
// Variables for communication
unsigned long SB_CommandPacket;
int SB_CommandMode;
int SB_BlueCommand;
int SB_RedCommand;
int SB_GreenCommand;
 
// Define number of ShiftBrite modules
#define NumLEDs 1
 
// Create LED value storage array
int LEDChannels[NumLEDs][3] = {0};
 
// Set pins to outputs and initial states
void setup() 
{
    pinMode(datapin, OUTPUT);
    pinMode(latchpin, OUTPUT);
    pinMode(enablepin, OUTPUT);
    pinMode(clockpin, OUTPUT);
    digitalWrite(latchpin, LOW);
    digitalWrite(enablepin, LOW);
    SPCR = (1 << SPE) | (1 << MSTR) | (0 << SPR1) | (0 << SPR0);
}
 
// Load values into SPI register
void SB_SendPacket() 
{
    if (SB_CommandMode == B01) 
    {
        SB_RedCommand = 127;
        SB_GreenCommand = 110;
        SB_BlueCommand = 110;
    }

    SPDR = SB_CommandMode << 6 | SB_BlueCommand >> 4;
    while(!(SPSR & (1 << SPIF)));
    SPDR = SB_BlueCommand << 4 | SB_RedCommand >> 6;
    while(!(SPSR & (1 << SPIF)));
    SPDR = SB_RedCommand << 2 | SB_GreenCommand >> 8;
    while(!(SPSR & (1 << SPIF)));
    SPDR = SB_GreenCommand;
    while(!(SPSR & (1 << SPIF)));
}
 
// Latch values into PWM registers
void SB_Latch() {
 
  delayMicroseconds(1);
  LATPORT += (1 << LATPIN);
  //ENAPORT += (1 << ENAPIN);
  delayMicroseconds(1);
  //ENAPORT &= ~(1 << ENAPIN);
  LATPORT &= ~(1 << LATPIN);
 
}
 
// Send all array values to chain
void WriteLEDArray() 
{
    // Write to PWM control registers
    SB_CommandMode = B00; 

    for (int i = 0; i < NumLEDs; ++i) 
    {
        SB_RedCommand = LEDChannels[i][0] & 1023;
        SB_GreenCommand = LEDChannels[i][1] & 1023;
        SB_BlueCommand = LEDChannels[i][2] & 1023;
        SB_SendPacket();
    }

    SB_Latch();

    // Write to current control registers
    SB_CommandMode = B01; 

    for (int z = 0; z < NumLEDs; ++z) 
    {
        SB_SendPacket();   
    }

    SB_Latch();
}
 
// Fade between two colors at specified interval
void fadeall(int rate, 
                int fromred, int fromgreen, int fromblue, 
                int tored, int togreen, int toblue)
{
    for (int i = 0; i < 33; i++) 
    {
        for (int j1 = 0; j1 < NumLEDs; j1++) 
        {
            LEDChannels[j1][0] = (fromred * (32 - i) + tored * i)/32;
            LEDChannels[j1][1] = (fromgreen * (32 - i) + togreen * i)/32;
            LEDChannels[j1][2] = (fromblue * (32 - i) + toblue * i)/32;
        }
        WriteLEDArray();
        delay(rate);
   }   
}
 
// Fade between two colors at specified interval
void pingpong(int rate) 
{
    int led_ptr = 0;
    int mark_ptr = 0;
    int op = 1;
    for (int i = 0; i < (NumLEDs * 2); ++i) 
    {
        for (int led_ptr = 0; led_ptr < NumLEDs; ++led_ptr) 
        {
            LEDChannels[led_ptr][0] = 0;
            LEDChannels[led_ptr][1] = 0;
            LEDChannels[led_ptr][2] = 0;
        }
        LEDChannels[mark_ptr][0] = random(1023);
        LEDChannels[mark_ptr][1] = random(1023);
        LEDChannels[mark_ptr][2] = random(1023);
        WriteLEDArray();
        delay(rate);
        mark_ptr = (mark_ptr + op);
        if(mark_ptr == NumLEDs || mark_ptr == 0)
            op = -op;
   }   
}
 
void loop()
{
    fadeall(90, 0, 0, 0, 1023, 0, 0);
    fadeall(90, 1023, 0, 0, 0, 1023, 0);
    fadeall(90, 0, 1023, 0, 0, 0, 1023);
    fadeall(90, 0, 0, 1023, 1023, 0, 0);
    fadeall(90, 1023, 0, 0, 0, 0, 0);
    delay(500);
    fadeall(60, 0, 0, 0, 0, 0, 1023);
    delay(500);
    fadeall(60, 0, 0, 1023, 0, 0, 0);  
    delay(500);
    // pingpong(200);
}


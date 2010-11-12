// Defines for use with Arduino functions
#define latchpin        9  // XL
#define enablepin       10 // BL
#define datapin         11 // SI
#define clockpin        13 // CL
 
// Defines for direct port access
#define CLKPORT         PORTB
#define ENAPORT         PORTB
#define LATPORT         PORTB
#define DATPORT         PORTB
#define CLKPIN          5
#define ENAPIN          2
#define LATPIN          1
#define DATPIN          3

// Sub Operations
#define CHAIN_LENGTH    1
#define CHAIN_LATCH     2
#define CHAIN_DISABLE   3
#define CHAIN_ENABLE    4
#define CHAIN_CONFIG    5

// Helper macros for frobbing bits
#define bitset(var, bitno) ((var) |= (1 << (bitno)))
#define bitclr(var, bitno) ((var) &= ~(1 << (bitno)))
#define bittst(var, bitno) (var& (1 << (bitno)))
 
// Runtime Globals
unsigned short chain_length = 0;

// Set pins to outputs and initial states
void setup() 
{
    Serial.begin(115200);
    pinMode(datapin, OUTPUT);
    pinMode(latchpin, OUTPUT);
    pinMode(enablepin, OUTPUT);
    pinMode(clockpin, OUTPUT);
    digitalWrite(latchpin, LOW);
    digitalWrite(enablepin, LOW);
    SPSR = (0 << SPI2X);
    SPCR = (1 << SPE) | (1 << MSTR) | (0 << SPR1) | (0 << SPR0);
    Serial.println("R");
}

/**
 *  Operations
 */

void disable_string() { digitalWrite(enablepin, HIGH); }
void enable_string() { digitalWrite(enablepin, LOW); }

// Latch values into PWM registers
void chain_latch() 
{
    delayMicroseconds(50);
    digitalWrite(latchpin, HIGH);
    delayMicroseconds(50);
    digitalWrite(latchpin, LOW);
}

void set_chain_length(byte length)
{
    chain_length = length;
}

__inline__ void wait_for_flush()
{
    unsigned char spif_flag = 1 << SPIF;
    while(!(SPSR & spif_flag))
    {}
}

__inline__ void send_ok()
{
    Serial.println("K");
}

void send_config()
{
    int config[4] = {1, 120, 100, 100};

    for(unsigned char idx = 0; idx < chain_length; ++idx)
    {
        SPDR = config[0] << 6 | config[1] >> 4;
        wait_for_flush();
        SPDR = config[1] << 4 | config[2] >> 6;
        wait_for_flush();
        SPDR = config[2] << 2 | config[3] >> 8;
        wait_for_flush();
        SPDR = config[3];
        wait_for_flush();
    }
    chain_latch();
}

void read_chain(byte b1)
{
    int chain_length_bytes = chain_length * 4;
    SPDR = b1;
    for(int idx = 1; idx < chain_length_bytes; ++idx)
    {
        SPDR = read_byte();
        wait_for_flush();
    }
}

/**
 *  USB Serial IO
 */

// read a single byte from the serial port
char __inline__ read_byte(void)
{
    wait_for_serial_input();
    return Serial.read();
}

// Sit and spin until there is serial data available
void __inline__ wait_for_serial_input()
{
    while (Serial.available() < 1) 
    {}
}

/**
 * Main Loop
 */
 
void loop()
{
    byte b1, b2;
    byte sub_op, op;

    b1 = read_byte();
    op = (b1 >> 6);
    if ((op == 0) || (op == 1))
    {
        read_chain(b1);
    } else if (op == 3)
    {
        sub_op = b1 & 0x3F;
        if (sub_op == CHAIN_LATCH)
        {
            chain_latch();
            send_ok();
        } else if (sub_op == CHAIN_LENGTH)
        {
            b2 = read_byte();
            set_chain_length(b2);
            send_ok();
        } else if (sub_op == CHAIN_DISABLE)
        {
            disable_string();
            send_ok();
        } else if (sub_op == CHAIN_ENABLE)
        {
            enable_string();
            send_ok();
        } else if (sub_op == CHAIN_CONFIG)
        {
            send_config();
            send_ok();
        } else
        {
            Serial.print("unk sub-op ");
            Serial.println(sub_op, DEC);
        }
    } else
    {
        Serial.print("unk op ");
        Serial.println(op, DEC);
    }
}

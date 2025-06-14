/*@authors vtrianni and cdimidov*/

#include <kilolib.h>
#define DEBUG
#if REAL
#define DEBUG
#include "debug.h"
#endif
#include <stdlib.h>
#include "enum.h"

//id target_info;
/*message transmited*/
message_t message;

/* Flag for decision to send a word */
bool msg_sent = false;

const uint8_t max_broadcast_ticks = 2 * 16; /* n_s*0.5*32 */
uint32_t last_broadcast_ticks = 0;

/*-------------------------------------------------------------------*/
/* Function to sent a message              */
/*-------------------------------------------------------------------*/
void broadcast()
{

    if (!msg_sent && kilo_ticks > last_broadcast_ticks + max_broadcast_ticks)
    {
        last_broadcast_ticks = kilo_ticks;
        // Reset the flag so the LED is only blinked once per message.
        msg_sent = true;
        //color the LED magenta
        set_color(RGB(1, 0, 1));
        /* send the message every 1 sec*/
        delay(100);
        set_color(RGB(0, 0, 0));
    }
}
/*-------------------------------------------------------------------*/
/* Callback function for message transmission                        */
/*-------------------------------------------------------------------*/
message_t *message_tx()
{
    if (msg_sent)
    {
        return &message;
    }
    return 0;
}

/*-------------------------------------------------------------------*/
/* Callback function for successful transmission                     */
/*-------------------------------------------------------------------*/
void tx_message_success()
{
    msg_sent = false;
}

void setup()
{

    /* Compute the message CRC value */
    message.data[0] = (uint8_t)id_target;
    message.type = NORMAL;
    message.crc = message_crc(&message);
}

void loop()
{
    broadcast();
}

int main()
{
    kilo_init();
    // Register the message_tx callback function.
    kilo_message_tx = message_tx;
    // Register the message_tx_success callback function.
    kilo_message_tx_success = tx_message_success;

#if REAL
    debug_init();
#endif

    kilo_start(setup, loop);

    return 0;
}

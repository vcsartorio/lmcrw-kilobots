/*@authors vtrianni and cdimidov*/

#include "kilolib.h"
#include <math.h>
#include "distribution_functions.c"
// ****************************************
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "enum.h"

#if REAL
#define DEBUG
#include <stdarg.h>
#include "debug.h"
#include <avr/eeprom.h>
#else
#include <inttypes.h>
#endif

//#define PI 3.141593

/* Enum for different motion types */
typedef enum
{
  STOP = 0,
  FORWARD,
  TURN_LEFT,
  TURN_RIGHT,
} motion_t;

/*variable that memorizes the first passage time and the time*/
uint32_t f_p_t = 0; // first passage time
uint32_t f_i_t = 0; // first moment when i received the information

/*CRW Parameters*/
const double CRW_exponent = CRW_EXPONENT;

/*LEVY Parameters*/
const double levy_exponent = LEVY_EXPONENT;

/*Max number of ticks*/
const double max_time = MAX_TIME;

/*STD*/
const double std_motion_steps = 5 * 16;

/* current motion type */
motion_t current_motion_type = STOP;

/*Message send to the others agents*/
message_t messageA;

/* Flag for decision to send a word */
bool sending_msg = false;

/*Flag for the existence of information*/
bool information_target_id = false;

/* Flag : send the id and first passage time to target */
bool on_target_flag = false;

/* counters for motion, turning and broadcasting */
uint32_t turning_ticks = 0;
const uint8_t max_turning_ticks = 160;
uint8_t max_straight_ticks = 0;
unsigned int straight_ticks = 0; /* 5*16; */ /* n_t*0.5*32 */
uint32_t last_motion_ticks = 0;
const uint8_t max_broadcast_ticks = 2 * 16; /* n_s*0.5*32 */
uint32_t last_broadcast_ticks = 0;
const uint16_t max_info_ticks = 7 * 16;
uint32_t last_info_ticks = 0;

void my_printf(const char *fmt, ...)
{
#if REAL
  va_list args;
  va_start(args, fmt);
  vprintf(fmt, args);

  va_end(args);
#endif
}

/*-------------------------------------------------------------------*/
/* Function for setting the motor speed                              */
/*-------------------------------------------------------------------*/
void set_motion(motion_t new_motion_type)
{
  if (kilo_ticks < max_time)
  {
    if (current_motion_type != new_motion_type)
    {
      switch (new_motion_type)
      {
      case FORWARD:
        spinup_motors();
        set_motors(kilo_straight_left, kilo_straight_right);
        break;
      case TURN_LEFT:
        spinup_motors();
        set_motors(kilo_turn_left, 0);
        break;
      case TURN_RIGHT:
        spinup_motors();
        set_motors(0, kilo_turn_right);
        break;
      case STOP:
      default:
        set_motors(0, 0);
      }
      current_motion_type = new_motion_type;
    }
  }
  else
  {
    set_motors(0, 0);
  }
}

/*-------------------------------------------------------------------*/
/* Init function                                                     */
/*-------------------------------------------------------------------*/
void setup()
{

  /* Initialise LED and motors */
  set_motors(0, 0);
  /* Initialise random seed */
  uint8_t seed = rand_hard();
  rand_seed(seed);
  srand(seed);
  f_i_t = 0;
  f_p_t = 0;
  /*Compute the message CRC value for the Target_id*/
  messageA.data[0] = (uint8_t)id_robot;
  /* Compute the message CRC value for the id */
  messageA.data[1] = 0; // 0 I don't have the message
  messageA.type = NORMAL;
  memset(&(messageA.data[1]), 0, 8);
  messageA.crc = message_crc(&messageA);

  /* Initialise motion variables */
  set_motion(FORWARD);
}
/*-------------------------------------------------------------------*/
/* Callback function for message transmission                        */
/*-------------------------------------------------------------------*/
message_t *message_tx()
{
  if (sending_msg)
  {
    return &messageA;
  }
  return 0;
}

/*-------------------------------------------------------------------*/
/* Callback function for successful transmission                     */
/*-------------------------------------------------------------------*/
void tx_message_success()
{
  sending_msg = false;
}

/*-------------------------------------------------------------------*/
/* Callback function for message reception                           */
/*-------------------------------------------------------------------*/
void message_rx(message_t *msg, distance_measurement_t *d)
{
  uint8_t cur_distance = estimate_distance(d);
  if (cur_distance > 100)
  {
    return;
  }
  uint8_t agent_type = msg->data[0] & 0x01;
  // my_printf("%u"
  // "\n",
  // agent_type);
  //if the message received is 0 so the id of the target set color red
  if (agent_type == id_target)
  {
    if (f_p_t == 0)
    {
      f_p_t = kilo_ticks;
      memcpy(((void *)(&(messageA.data[5]))), &f_p_t, sizeof(int32_t));
      messageA.crc = message_crc(&messageA);

      // my_printf("The kilobot is on target for the first time\n");
      // my_printf("%" PRIu32 "\n", f_p_t);
      information_target_id = true;
      set_color(RGB(3, 0, 3));
    }
    if (f_i_t == 0)
    {
      f_i_t = kilo_ticks;
      memcpy(((void *)(&(messageA.data[1]))), &f_i_t, sizeof(int32_t));
      messageA.crc = message_crc(&messageA);

      // my_printf("The kilobot has the information but cross the target for the first time \n");
      // my_printf("%" PRIu32 "\n", f_i_t);
    }
  }
  //if the message received is 1 so the id of the target set color green
  else if (agent_type == id_robot)
  {
    // my_printf("%u"
    // "\n",
    // agent_type);
    if (f_i_t == 0)
    {
      f_i_t = kilo_ticks;
      memcpy(((void *)(&(messageA.data[1]))), &f_i_t, sizeof(int32_t));
      messageA.crc = message_crc(&messageA);
      // my_printf("The kilobot receive information from the other robot\n");
      // my_printf("%" PRIu32 "\n", f_i_t);
      information_target_id = true;
      set_color(RGB(0, 3, 0));
    }
  }
}

/*-------------------------------------------------------------------*/
/* Function to send a message                                        */
/*-------------------------------------------------------------------*/
void broadcast()
{

  if (information_target_id && !sending_msg && kilo_ticks > last_broadcast_ticks + max_broadcast_ticks)
  {
    last_broadcast_ticks = kilo_ticks;
    sending_msg = true;
  }
}
/*----------------------------------------------------------------------*/
/* Function implementing the correlated random walk and levy random walk*/
/*----------------------------------------------------------------------*/
void random_walk()
{
  if (kilo_ticks < max_time)
  {
    switch (current_motion_type)
    {
    case TURN_LEFT:
    case TURN_RIGHT:
      if (kilo_ticks > last_motion_ticks + turning_ticks)
      {
        /* start moving forward */
        last_motion_ticks = kilo_ticks;
        set_motion(FORWARD);
      }
      break;
    case FORWARD:
      if (kilo_ticks > last_motion_ticks + straight_ticks)
      {
        /* perform a random turn */
        last_motion_ticks = kilo_ticks;
        if (rand_soft() % 2)
        {
          set_motion(TURN_LEFT);
        }
        else
        {
          set_motion(TURN_RIGHT);
        }
        double angle = 0;
        if (CRW_exponent == 0)
        {

          angle = (uniform_distribution(0, (M_PI)));
          // my_printf("%" PRIu32 "\n", turning_ticks);
          // my_printf("%u" "\n", rand());
        }
        else
        {
          angle = fabs(wrapped_cauchy_ppf(CRW_exponent));
        }
        turning_ticks = (uint32_t)((angle / M_PI) * max_turning_ticks);
        straight_ticks = (uint32_t)(fabs(levy(std_motion_steps, levy_exponent)));
        // my_printf("%u" "\n", straight_ticks);
      }
      break;

    case STOP:
    default:
      set_motion(STOP);
    }
  }
  else
  {
    set_motion(STOP);
  }
}

void kilobotinfo()
{
  if (kilo_ticks > last_info_ticks + max_info_ticks)
  {
    last_info_ticks = kilo_ticks;
    my_printf("FPT:");
    my_printf("%" PRIu32 "\n", f_p_t);
    my_printf("Interaction Time:");
    my_printf("%" PRIu32 "\n", f_i_t);
  }
}

void check_reset()
{
  if (kilo_ticks == 0) // NOT THE RIGHT TEST, kilo_tick doesnt reinitiate?
  {
    setup();
  }
}

/*-------------------------------------------------------------------*/
/* Main loop                                                         */
/*-------------------------------------------------------------------*/
void loop()
{
  check_reset();
  random_walk();
  broadcast();
  kilobotinfo();
}

/*-------------------------------------------------------------------*/
/* Main function                                                     */
/*-------------------------------------------------------------------*/
int main()
{
  kilo_init();
  kilo_message_rx = message_rx;
  kilo_message_tx = message_tx;
  kilo_message_tx_success = tx_message_success;

#if REAL
  debug_init();
#endif

  /* start main loop */
  kilo_start(setup, loop);

  return 0;
}

// Includes
#include "main.h"
#include "lwip.h"
#include "udp.h"
#include "usb_device.h"

#define frequency 10	// Data sending frequency ( Important for minimum sequence delay and flowrate measurements)
#define MAX_MESSAGE_LENGTH 600	// Length of sequence message
#define purge_time 1000 // Time (in ms) for the purge (for emergency purpose)

// Name of ADC, DMA, Timer
ADC_HandleTypeDef hadc1;
DMA_HandleTypeDef hdma_adc1;
TIM_HandleTypeDef htim2;

// Parameters for udp ethernet connection
struct udp_pcb *udp_pcb;
struct pbuf *p;
ip_addr_t dest_ip;
ip_addr_t my_ip;
char address[] = "192.168.1.101";	// Computer IP address (ethernet address)
uint16_t udp_port = 12345;	// Computer communication port

// Pressure parameters
uint32_t Pressure_Sensor[3];	// Store pressure data

// Parameters used for flow rate computation
volatile int pulseCountFS1 = 0;  // Number of pulsation registered during certain time for the first flowrate sensor
volatile int pulseCountFS2 = 0;  // Number of pulsation registered during certain time for the second flowrate sensor
unsigned long flowrateTime = 0;  // Reference time for flowrate measurement
const float calibrationFactor = 318.7747222f; // Calibration factor found experimentally
volatile uint32_t FS1 = 0;  // Flowrate value (in L/s)
volatile uint32_t FS2 = 0;  // Flowrate value (in L/s)

// Flags
volatile uint8_t sparkFlag = 0; // 0: stop sparking, 1: start sparking
volatile uint8_t sequenceFlag = 0; // 0: stop sequence, 1: start sequence
volatile uint32_t emergencyFlag = 0; // 0: stop emergency, 1: start emergency

// Sequence
volatile uint32_t sequenceTime = 0; // Reference time for sequence execution

// Valve status and control
volatile uint8_t valveStatus = 0; // 7-digit binary number to register valve status (value sent by computer)
volatile uint8_t bit0, bit1, bit2, bit3, bit4, bit5, bit6;  // Bits of the valveStatus (used to track the evolution of the valve satus -- sent to computer)
uint16_t list0[MAX_MESSAGE_LENGTH] = {0}; // EV0 sequence
uint16_t list1[MAX_MESSAGE_LENGTH] = {0}; // EV1 sequence
uint16_t list2[MAX_MESSAGE_LENGTH] = {0}; // EV2 sequence
uint16_t list3[MAX_MESSAGE_LENGTH] = {0}; // EV3 sequence
uint16_t list4[MAX_MESSAGE_LENGTH] = {0}; // EV4 sequence
uint16_t list5[MAX_MESSAGE_LENGTH] = {0}; // EV5 sequence
uint16_t list6[MAX_MESSAGE_LENGTH] = {0}; // EV6 sequence


void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_DMA_Init(void);
static void MX_ADC1_Init(void);
static void MX_TIM2_Init(void);
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin);
extern void HAL_GPIO_EXTI_IRQHandler(uint16_t GPIO_Pin);
void udp_receive_callback(void *arg, struct udp_pcb *pcb, struct pbuf *p, const ip_addr_t *addr, u16_t port);
void emergency(void);
void transmit_sensor_values(void);
void get_values(void);
void sequence(void);
void spark(void);
void parseAndStore(char *message);
void removeProcessedValue(uint16_t *list);

// Main
int main(void)
{
  // Initialisation of the multiple libraries used
  HAL_Init();
  SystemClock_Config();
  MX_GPIO_Init();
  MX_DMA_Init();
  MX_ADC1_Init();
  MX_TIM2_Init();
  MX_LWIP_Init(); // Ethernet
  MX_USB_DEVICE_Init();

  // Ping STM variable
  extern struct netif gnetif;

  // Convert address string to IP address
  ipaddr_aton(address, &dest_ip);

  // Create a new UDP control block
  udp_pcb = udp_new();
  if (udp_pcb != NULL)
  {
      // Bind UDP to any IP address and specified port
      udp_bind(udp_pcb, IP_ADDR_ANY, udp_port);
  }

  // Set STM32 IP address
  IP4_ADDR(&my_ip, 192, 168, 1, 100);

  // Register callback for incoming UDP packets
  udp_recv(udp_pcb, udp_receive_callback, NULL);

  // Set the reference time for flowrate measurements
  flowrateTime = HAL_GetTick();
  while (1)
  {
	  // Used to ping the STM
    ethernetif_input(&gnetif);
    sys_check_timeouts();

    // Flag --> sequence launched
    if (sequenceFlag)
    {
    	sequence();
	  }

    // Flag --> emergency launched
    if (emergencyFlag)
    {
    	emergencyFlag=0;
    	emergency();
    }

    get_values();

    spark();

  }
}

//--------------------------------------------------------------------
//                Sensor related functions
//--------------------------------------------------------------------
// Send all the sensor data to the computer
void transmit_sensor_values() {
    uint32_t PS1 = (uint32_t)(Pressure_Sensor[0]);  // C3H8 pressure
    uint32_t PS2 = (uint32_t)(Pressure_Sensor[1]);  // GOX pressure
    uint32_t PS3 = (uint32_t)(Pressure_Sensor[2]);  // N2 pressure
    uint32_t TS1 = (uint32_t)(0); // C3H8 temperature
    uint32_t TS2 = (uint32_t)(0); // GOX temperature
    uint32_t time = HAL_GetTick();  // Sending time

    // Buffer that contains the data that will be sent (pressure, temperature, flowrate, valve status)
    char sensor_buffer[256];
    sprintf(sensor_buffer, "time=%lu,PS1=%lu,PS2=%lu,PS3=%lu,TS1=%lu,TS2=%lu,FS1=%lu,FS2=%lu,EV0=%lu"
    		",EV1=%lu,EV2=%lu,EV3=%lu,EV4=%lu,EV5=%lu,EV6=%lu\n\r",
    		time,PS1,PS2,PS3,TS1,TS2,FS1,FS2, bit6, bit5, bit4, bit3, bit2, bit1,bit0);

    // Allocate pbuf
    p = pbuf_alloc(PBUF_TRANSPORT, strlen(sensor_buffer), PBUF_RAM);
    if (p != NULL) {
        // Copy data to pbuf
        pbuf_take(p, sensor_buffer, strlen(sensor_buffer));
        // Send the buffer over UDP
        udp_sendto(udp_pcb, p, &dest_ip, udp_port);
        // Free the pbuf
        pbuf_free(p);
    }
}

// Read the sensor values
void get_values()
{
	unsigned long currentTime = HAL_GetTick();  // Reference time
	unsigned long elapsedTime = currentTime - flowrateTime; // Elapsed time since last sending of values
	int t = 1000/frequency; // Delay (in ms) between each sending
  /*
  The "frequency" variable (and time) is a critical variable. It decides the rate at which the STM sends data, the sparking frequency but also the minimum delay that must be set for the valve sequence.
  CAUTION : If the time between two toggles of one or multiple valves is smaller than the variable "t", the second toggle will not happen at the expected time (some shift will therefore occur)

  The flowrate sensor measures the flowrate by counting pulses over a certain time.
  - The flowrate sensor sends a pulse
  - This pulse is detected by the GPIO port which increases a counter
  - When the "elapsedTime" is greater than the threshold time, the flowrate is computed based on the counter
  If the frequency is too high, the accuracy of the sensor might be affected so considered
  */
	if (elapsedTime > t)
	{
		__disable_irq(); // Disable interrupts during critical section
	    // Calculate flowrates
	    FS1 = 1000.0f *(((1000.0f / elapsedTime) * pulseCountFS1) / calibrationFactor);
	    FS2 = 1000.0f *(((1000.0f / elapsedTime) * pulseCountFS2) / calibrationFactor);
	    pulseCountFS1 = 0;  // Reset counter
	    pulseCountFS2 = 0;  // Reset counter
	    flowrateTime = currentTime;
	    __enable_irq(); // Enable interrupts
		HAL_ADC_Start_DMA(&hadc1, Pressure_Sensor, 3);	// Read ADC for pressure values
		transmit_sensor_values();
	 }
}

//--------------------------------------------------------------------
//                Listening related function
//--------------------------------------------------------------------
// Listen to any message sent by the computer -- This function has the highest priority meaning that any ongoing action will be interrupt if a message is received
void udp_receive_callback(void *arg, struct udp_pcb *pcb, struct pbuf *p, const ip_addr_t *addr, u16_t port)
{
	struct pbuf *response_pbuf; // Acknowledgement buffer
	const char *response_msg = "OK";  // Acknowledgement message

  // Detect if a message has been received
	if (p != NULL)
	{
    // Command buffer (for spark and emergency)
    char msg[100];
    strncpy(msg, (char*)p->payload, p->len);
    msg[p->len] = '\0';

    // Emergency condition / Triggers the emergency flag and send back a response for acknowledgement
    if (strcmp(msg, "STOP") == 0)
    {
    	emergencyFlag = 1;

    	response_pbuf = pbuf_alloc(PBUF_TRANSPORT, strlen(response_msg), PBUF_RAM);
    	if (response_pbuf != NULL)
    	{
    		memcpy(response_pbuf->payload, response_msg, strlen(response_msg));
    		// Send the response back to the sender
    		udp_sendto(udp_pcb, response_pbuf,&dest_ip, udp_port);
    		// Free the response pbuf
    		pbuf_free(response_pbuf);
    	}
    }

    // Spark condition / Triggers the spark flag and send back a response for acknowledgement
    else if (strcmp(msg, "SP") == 0)
    {
      sparkFlag = 1;

      response_pbuf = pbuf_alloc(PBUF_TRANSPORT, strlen(response_msg), PBUF_RAM);
      if (response_pbuf != NULL)
      {
        memcpy(response_pbuf->payload, response_msg, strlen(response_msg));
        // Send the response back to the sender
        udp_sendto(udp_pcb, response_pbuf, &dest_ip, udp_port);
        // Free the response pbuf
        pbuf_free(response_pbuf);
      }
    }

    // Unspark condition / Triggers the spark flag and send back a response for acknowledgement
    else if (strcmp(msg, "UNSP") == 0)
    {
      sparkFlag = 0; // Set flag to stop sparking

      response_pbuf = pbuf_alloc(PBUF_TRANSPORT, strlen(response_msg), PBUF_RAM);
      if (response_pbuf != NULL)
      {
        memcpy(response_pbuf->payload, response_msg, strlen(response_msg));
        // Send the response back to the sender
        udp_sendto(udp_pcb, response_pbuf, &dest_ip, udp_port);
        // Free the response pbuf
        pbuf_free(response_pbuf);
      }
    }

    // Valve control using binary
    else if (p->len == 7)
    {
      char binary_string[9];
      memset(binary_string, 0, sizeof(binary_string));
      memcpy(binary_string, p->payload, p->len < 8 ? p->len : 8); // Copy the payload to the buffer

      // Convert the binary string to a byte value
      valveStatus = (uint8_t)strtol(binary_string, NULL, 2);

      // Extract each bit from valveStatus
      bit0 = (valveStatus >> 0) & 0x01;
      bit1 = (valveStatus >> 1) & 0x01;
      bit2 = (valveStatus >> 2) & 0x01;
      bit3 = (valveStatus >> 3) & 0x01;
      bit4 = (valveStatus >> 4) & 0x01;
      bit5 = (valveStatus >> 5) & 0x01;
      bit6 = (valveStatus >> 6) & 0x01;

      // Sends a voltage on the ports depending on the bit (1 : activate / 0 : deactivate)
      HAL_GPIO_WritePin(GPIOF, GPIO_PIN_13, (valveStatus & 0x01) ? GPIO_PIN_SET : GPIO_PIN_RESET);	//NC
      HAL_GPIO_WritePin(GPIOE, GPIO_PIN_9, (valveStatus & 0x02) ? GPIO_PIN_SET : GPIO_PIN_RESET);	//NC
      HAL_GPIO_WritePin(GPIOE, GPIO_PIN_11, (valveStatus & 0x04) ? GPIO_PIN_SET : GPIO_PIN_RESET);	//NC
      HAL_GPIO_WritePin(GPIOF, GPIO_PIN_14, (valveStatus & 0x08) ? GPIO_PIN_SET : GPIO_PIN_RESET);	//NC
      HAL_GPIO_WritePin(GPIOE, GPIO_PIN_13, (valveStatus & 0x10) ? GPIO_PIN_RESET : GPIO_PIN_SET);	//NO
      HAL_GPIO_WritePin(GPIOF, GPIO_PIN_15, (valveStatus & 0x20) ? GPIO_PIN_SET : GPIO_PIN_RESET);	//NC
      HAL_GPIO_WritePin(GPIOG, GPIO_PIN_14, (valveStatus & 0x40) ? GPIO_PIN_SET : GPIO_PIN_RESET);	//NC
      pbuf_free(p);

      response_pbuf = pbuf_alloc(PBUF_TRANSPORT, strlen(response_msg), PBUF_RAM);
      if (response_pbuf != NULL)
      {
        memcpy(response_pbuf->payload, response_msg, strlen(response_msg));
        // Send the response back to the sender
        udp_sendto(udp_pcb, response_pbuf, &dest_ip, udp_port);
        // Free the response pbuf
        pbuf_free(response_pbuf);
      }
    }

    // Parse and store the message in multiple array and trigger sequence flag (+ sparking)
    else if(p->len > 7)
    {
      char message[1000] = {0};
      strncpy(message, (char*)p->payload, p->len);
      pbuf_free(p);
      sparkFlag=1;
      sequenceFlag=1;
      parseAndStore(message);
      sequenceTime = HAL_GetTick(); // Reference time of the test

      response_pbuf = pbuf_alloc(PBUF_TRANSPORT, strlen(response_msg), PBUF_RAM);
    	if (response_pbuf != NULL)
    	{
    		memcpy(response_pbuf->payload, response_msg, strlen(response_msg));
    		// Send the response back to the sender
    		udp_sendto(udp_pcb, response_pbuf, &dest_ip, udp_port);
    		// Free the response pbuf
    		pbuf_free(response_pbuf);
    	}
    }
	}
}

//--------------------------------------------------------------------
//                Sequence related functions
//--------------------------------------------------------------------
// Sequence control
void sequence()
{
	uint32_t previousTick = HAL_GetTick();
  // Check for emergency
	if (emergencyFlag)
	{
		sequenceFlag=0;
		sparkFlag=0;
	}
  else
  {
    /*
    Change the state of the valve, register it in its corresponding bit and remove the time from the array
    Toggle GPIO port if the time since the starting of the test is greater than the time register in the list (and the registered time is not 0)
    */
    if (previousTick-sequenceTime>list0[0] && list0[0]!=0)
    {
      HAL_GPIO_TogglePin(GPIOF, GPIO_PIN_13);
      bit0 ^= 1;
      removeProcessedValue(list0);
    }

    if (previousTick-sequenceTime>list1[0] && list1[0]!=0)
    {
      HAL_GPIO_TogglePin(GPIOE, GPIO_PIN_9);
      bit1 ^= 1;
      removeProcessedValue(list1);
    }

    if (previousTick-sequenceTime>list2[0] && list2[0]!=0)
    {
      HAL_GPIO_TogglePin(GPIOE, GPIO_PIN_11);
      bit2 ^= 1;
      removeProcessedValue(list2);
    }
    if (previousTick-sequenceTime>list3[0] && list3[0]!=0)
    {
      HAL_GPIO_TogglePin(GPIOF, GPIO_PIN_14);
      bit3 ^= 1;
      removeProcessedValue(list3);
    }

    if (previousTick-sequenceTime>list4[0] && list4[0]!=0)
    {
      HAL_GPIO_TogglePin(GPIOE, GPIO_PIN_13);
      bit4 ^= 1;
      removeProcessedValue(list4);
    }

    if (previousTick-sequenceTime>list5[0] && list5[0]!=0)
    {
      HAL_GPIO_TogglePin(GPIOF, GPIO_PIN_15);
      bit5 ^= 1;
      removeProcessedValue(list5);
    }
    if (previousTick-sequenceTime>list6[0] && list6[0]!=0)
    {
      HAL_GPIO_TogglePin(GPIOG, GPIO_PIN_14);
      bit6 ^= 1;
      removeProcessedValue(list6);
    }

    // If all the list have zeroes, the sequence is considered finished
    if (list0[0]==0 && list1[0]==0 && list2[0]==0 && list3[0]==0 && list4[0]==0 && list5[0]==0 && list6[0]==0)
    {
      sparkFlag=0;
      sequenceFlag=0;

      // Confirm the end of the sequence
      struct pbuf *sequence_pbuf;
	    const char *sequence_msg = "DONE";

      sequence_pbuf = pbuf_alloc(PBUF_TRANSPORT, strlen(sequence_msg), PBUF_RAM);
    	if (sequence_pbuf != NULL)
    	{
    		memcpy(sequence_pbuf->payload, sequence_msg, strlen(sequence_msg));
    		// Send the response back to the sender
    		udp_sendto(udp_pcb, sequence_pbuf, &dest_ip, udp_port);
    		// Free the response pbuf
    		pbuf_free(sequence_pbuf);
    	}
    }
  }
}

// Parse the message into multiple arrays
void parseAndStore(char *message)
{
    char *token;
    int listIndex = 0;
    int currentList = 0; // Start storing in list1

    // Parse the message using strtok
    token = strtok(message, ",");
    while (token != NULL)
    {
        if (strcmp(token, "E") == 0)
        {
            currentList++; // Switch to the next list
            listIndex = 0;
        }
        else
        {
            // Convert token to integer and store in current list
            uint16_t number = atoi(token);
            switch (currentList)
            {
                case 1:
                    list0[listIndex++] = number;
                    break;
                case 2:
                    list1[listIndex++] = number;
                    break;
                case 3:
                    list2[listIndex++] = number;
                    break;
                case 4:
                    list3[listIndex++] = number;
                    break;
                case 5:
                    list4[listIndex++] = number;
                    break;
                case 6:
                    list5[listIndex++] = number;
                    break;
                case 7:
                    list6[listIndex++] = number;
                    break;
                default:
                    break;
            }
        }
        token = strtok(NULL, ",");
    }
}

// Remove time value once used for sequence
void removeProcessedValue(uint16_t *list)
{
  for (int i = 0; i < MAX_MESSAGE_LENGTH - 1; i++)
  {
    list[i] = list[i + 1];
  }
  list[MAX_MESSAGE_LENGTH - 1] = 0;
}

//--------------------------------------------------------------------
//                Other command related functions
//--------------------------------------------------------------------
// Spark control
void spark()
{
  if (sparkFlag)
  {
    HAL_GPIO_TogglePin(GPIOG, GPIO_PIN_9);
    HAL_Delay(1000 / frequency);
  }
}

// Emergency function (Stop all ongoing actions and perform emergency procedure)
void emergency()
{
  // Close all the valves
	HAL_GPIO_WritePin(GPIOF, GPIO_PIN_13,GPIO_PIN_RESET);	//NC
	HAL_GPIO_WritePin(GPIOE, GPIO_PIN_9,GPIO_PIN_RESET);	//NC
	HAL_GPIO_WritePin(GPIOE, GPIO_PIN_11,GPIO_PIN_RESET);	//NC
	HAL_GPIO_WritePin(GPIOF, GPIO_PIN_14,GPIO_PIN_RESET);	//NC
	HAL_GPIO_WritePin(GPIOE, GPIO_PIN_13,GPIO_PIN_SET);	//NO
	HAL_GPIO_WritePin(GPIOF, GPIO_PIN_15,GPIO_PIN_RESET);	//NC
	HAL_GPIO_WritePin(GPIOG, GPIO_PIN_14,GPIO_PIN_RESET);	//NC

  // Set the bits of the valves (sent to computer)
  bit0=0;
	bit1=0;
	bit2=0;
	bit3=0;
	bit4=1;
	bit5=0;
	bit6=0;
	HAL_Delay(10);

  // Open purge valve for a certain time
	HAL_GPIO_WritePin(GPIOG, GPIO_PIN_14,GPIO_PIN_SET);
	HAL_Delay(purge_time);
	HAL_GPIO_WritePin(GPIOG, GPIO_PIN_14,GPIO_PIN_RESET);
}

void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLM = 8;
  RCC_OscInitStruct.PLL.PLLN = 240;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;
  RCC_OscInitStruct.PLL.PLLQ = 5;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV4;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV2;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_3) != HAL_OK)
  {
    Error_Handler();
  }
}

static void MX_ADC1_Init(void)
{
  ADC_ChannelConfTypeDef sConfig = {0};

  hadc1.Instance = ADC1;
  hadc1.Init.ClockPrescaler = ADC_CLOCK_SYNC_PCLK_DIV2;
  hadc1.Init.Resolution = ADC_RESOLUTION_12B;
  hadc1.Init.ScanConvMode = ENABLE;
  hadc1.Init.ContinuousConvMode = DISABLE;
  hadc1.Init.DiscontinuousConvMode = DISABLE;
  hadc1.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_NONE;
  hadc1.Init.ExternalTrigConv = ADC_SOFTWARE_START;
  hadc1.Init.DataAlign = ADC_DATAALIGN_RIGHT;
  hadc1.Init.NbrOfConversion = 3;
  hadc1.Init.DMAContinuousRequests = ENABLE;
  hadc1.Init.EOCSelection = ADC_EOC_SINGLE_CONV;
  if (HAL_ADC_Init(&hadc1) != HAL_OK)
  {
    Error_Handler();
  }

  sConfig.Channel = ADC_CHANNEL_3;
  sConfig.Rank = 1;
  sConfig.SamplingTime = ADC_SAMPLETIME_3CYCLES;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }

  sConfig.Channel = ADC_CHANNEL_10;
  sConfig.Rank = 2;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }

  sConfig.Channel = ADC_CHANNEL_13;
  sConfig.Rank = 3;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
}

static void MX_TIM2_Init(void)
{
  TIM_ClockConfigTypeDef sClockSourceConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};

  htim2.Instance = TIM2;
  htim2.Init.Prescaler = 0;
  htim2.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim2.Init.Period = 65535;
  htim2.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim2.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_ENABLE;
  if (HAL_TIM_Base_Init(&htim2) != HAL_OK)
  {
    Error_Handler();
  }
  sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
  if (HAL_TIM_ConfigClockSource(&htim2, &sClockSourceConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim2, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
}

static void MX_DMA_Init(void)
{
  __HAL_RCC_DMA2_CLK_ENABLE();

  HAL_NVIC_SetPriority(DMA2_Stream0_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(DMA2_Stream0_IRQn);

}

static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};

  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOH_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();
  __HAL_RCC_GPIOF_CLK_ENABLE();
  __HAL_RCC_GPIOE_CLK_ENABLE();
  __HAL_RCC_GPIOD_CLK_ENABLE();
  __HAL_RCC_GPIOG_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOB, LD1_Pin|LD3_Pin|LD2_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOF, GPIO_PIN_13|GPIO_PIN_14|GPIO_PIN_15, GPIO_PIN_RESET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOE, GPIO_PIN_9|GPIO_PIN_11|GPIO_PIN_13, GPIO_PIN_RESET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOG, USB_PowerSwitchOn_Pin|GPIO_PIN_9|GPIO_PIN_14, GPIO_PIN_RESET);

  /*Configure GPIO pin : USER_Btn_Pin */
  GPIO_InitStruct.Pin = USER_Btn_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(USER_Btn_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pins : LD1_Pin LD3_Pin LD2_Pin */
  GPIO_InitStruct.Pin = LD1_Pin|LD3_Pin|LD2_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

  /*Configure GPIO pins : PF13 PF14 PF15 */
  GPIO_InitStruct.Pin = GPIO_PIN_13|GPIO_PIN_14|GPIO_PIN_15;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOF, &GPIO_InitStruct);

  /*Configure GPIO pins : PE9 PE11 PE13 */
  GPIO_InitStruct.Pin = GPIO_PIN_9|GPIO_PIN_11|GPIO_PIN_13;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOE, &GPIO_InitStruct);

  /*Configure GPIO pins : STLK_RX_Pin STLK_TX_Pin */
  GPIO_InitStruct.Pin = STLK_RX_Pin|STLK_TX_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
  GPIO_InitStruct.Alternate = GPIO_AF7_USART3;
  HAL_GPIO_Init(GPIOD, &GPIO_InitStruct);

  /*Configure GPIO pins : USB_PowerSwitchOn_Pin PG9 PG14 */
  GPIO_InitStruct.Pin = USB_PowerSwitchOn_Pin|GPIO_PIN_9|GPIO_PIN_14;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOG, &GPIO_InitStruct);

  /*Configure GPIO pin : USB_OverCurrent_Pin */
  GPIO_InitStruct.Pin = USB_OverCurrent_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(USB_OverCurrent_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pins : PB8 PB9 */
  GPIO_InitStruct.Pin = GPIO_PIN_8|GPIO_PIN_9;
  GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);
  HAL_NVIC_SetPriority(EXTI9_5_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(EXTI9_5_IRQn);
}

// Define an interrupt when a pulse is detected on a GPIO port (function with the second highest priority)
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
  if (GPIO_Pin == GPIO_PIN_8) {
	  pulseCountFS1++;
  }
  if (GPIO_Pin == GPIO_PIN_9) {
	  pulseCountFS2++;
  }
}

// Connect the interruption handler with the GPIO port
void EXTI9_5_IRQHandler(void)
{
  HAL_GPIO_EXTI_IRQHandler(GPIO_PIN_8);
  HAL_GPIO_EXTI_IRQHandler(GPIO_PIN_9);
}

void Error_Handler(void)
{
  __disable_irq();
  while (1)
  {
  }
}

#ifdef  USE_FULL_ASSERT
void assert_failed(uint8_t *file, uint32_t line)
{
}
#endif

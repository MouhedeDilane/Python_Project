################################################################################
# Automatically-generated file. Do not edit!
# Toolchain: GNU Tools for STM32 (12.3.rel1)
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
C:/STM32_project/Main_V2/USB_DEVICE/Target/usbd_conf.c 

OBJS += \
./Application/User/USB_DEVICE/Target/usbd_conf.o 

C_DEPS += \
./Application/User/USB_DEVICE/Target/usbd_conf.d 


# Each subdirectory must supply rules for building sources it contributes
Application/User/USB_DEVICE/Target/usbd_conf.o: C:/STM32_project/Main_V2/USB_DEVICE/Target/usbd_conf.c Application/User/USB_DEVICE/Target/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m3 -std=gnu11 -g3 -DDEBUG -DUSE_HAL_DRIVER -DSTM32F207xx -c -I../../LWIP/App -I../../LWIP/Target -I../../USB_DEVICE/App -I../../USB_DEVICE/Target -I../../Core/Inc -I../../Middlewares/Third_Party/LwIP/src/include -I../../Middlewares/Third_Party/LwIP/system -I../../Drivers/STM32F2xx_HAL_Driver/Inc -I../../Drivers/STM32F2xx_HAL_Driver/Inc/Legacy -I../../Middlewares/Third_Party/LwIP/src/include/netif/ppp -I../../Middlewares/ST/STM32_USB_Device_Library/Core/Inc -I../../Middlewares/ST/STM32_USB_Device_Library/Class/CDC/Inc -I../../Drivers/CMSIS/Device/ST/STM32F2xx/Include -I../../Middlewares/Third_Party/LwIP/src/include/lwip -I../../Middlewares/Third_Party/LwIP/src/include/lwip/apps -I../../Middlewares/Third_Party/LwIP/src/include/lwip/priv -I../../Middlewares/Third_Party/LwIP/src/include/lwip/prot -I../../Middlewares/Third_Party/LwIP/src/include/netif -I../../Middlewares/Third_Party/LwIP/src/include/posix -I../../Middlewares/Third_Party/LwIP/src/include/posix/sys -I../../Middlewares/Third_Party/LwIP/system/arch -I../../Drivers/CMSIS/Include -O0 -ffunction-sections -fdata-sections -Wall -fstack-usage -fcyclomatic-complexity -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfloat-abi=soft -mthumb -o "$@"

clean: clean-Application-2f-User-2f-USB_DEVICE-2f-Target

clean-Application-2f-User-2f-USB_DEVICE-2f-Target:
	-$(RM) ./Application/User/USB_DEVICE/Target/usbd_conf.cyclo ./Application/User/USB_DEVICE/Target/usbd_conf.d ./Application/User/USB_DEVICE/Target/usbd_conf.o ./Application/User/USB_DEVICE/Target/usbd_conf.su

.PHONY: clean-Application-2f-User-2f-USB_DEVICE-2f-Target


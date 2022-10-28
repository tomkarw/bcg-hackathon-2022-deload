from energy_status import EnergyStatus
from gpiozero import Button, LED, CPUTemperature
import time

import board
import adafruit_dht
import logging

temperature_sensor = adafruit_dht.DHT11(board.D17)

lightsensor = Button(2)
old_lightsensor_state = not lightsensor.is_pressed

green = LED(27)
yellow = LED(3)
red = LED(4)
green.off()
red.on()

logging.basicConfig(level=logging.DEBUG)


def update_energy_status() -> EnergyStatus:
    if lightsensor.is_pressed:
        yellow.on()
    else:
        yellow.off()
    return EnergyStatus(
        light=lightsensor.is_pressed,
        environment_temperature=read_temperature_sensor(),
        cpu_temperature=CPUTemperature().temperature,
    )


def read_temperature_sensor():
    try:
        temp = temperature_sensor.temperature
        print(f"Temperature {temp}")
        return temp
    except RuntimeError as error:
        print(error.args[0])
    except Exception as error:
        temperature_sensor.exit()
        raise error


def act_compute_on():
    logging.info("COMPUTE ON")
    green.on()
    red.off()


def act_compute_off():
    logging.info("COMPUTE OFF")
    green.off()
    red.on()
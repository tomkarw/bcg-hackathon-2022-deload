from dataclasses import asdict, dataclass
import socketio
import time
import random
from energy_status import EnergyStatus
from main_node import energy_status

from monte_carlo_status import MonteCarloStatus

from gpiozero import Button, LED
import time

import board
import adafruit_dht

temperature_sensor = adafruit_dht.DHT11(board.D17)

lightsensor = Button(2)
old_lightsensor_state = not lightsensor.is_pressed

sio = socketio.Client()

SERVER_URL = "http://localhost:8080"
DEBUG = True

green = LED(3)
red = LED(4)
green.off()
red.on()

is_active = False
compute_result = MonteCarloStatus(0, 0)


@sio.on("compute_on")
def on_message(data):
    compute_result = MonteCarloStatus(data.count_in, data.count_out)
    is_active = True
    green.on()
    red.off()


@sio.on("compute_off")
def on_message(data):
    is_active = False
    send_result(compute_result)
    green.off()
    red.on()


@sio.on("get_result")
def on_message():
    send_result(compute_result)


def send_result(result: MonteCarloStatus):
    sio.emit("result", result.toJson())


@sio.on("*")
def catch_all(event, data):
    print("Received non-standard event")


sio.connect(SERVER_URL)
print("my sid is", sio.sid)


def monte_carlo_step(status: MonteCarloStatus):
    rand_x = random.uniform(-1, 1)
    rand_y = random.uniform(-1, 1)

    origin_dist = rand_x**2 + rand_y**2

    # Checking if (x, y) lies inside the circle
    if origin_dist <= 1:
        status.count_in += 1

    status.count_out += 1

    if DEBUG:
        print(f"Current Approx: {4 * status.count_in / status.count_out}")

    return status


def update_energy_status():
    current_energy_status.light = lightsensor.is_pressed
    current_energy_status.environment_temperature = read_temperature_sensor()
    sio.emit("energy_status", current_energy_status.as_json())

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


current_monte_carlos_status = MonteCarloStatus(0, 0)
current_energy_status = EnergyStatus(0, 100, 100)

while True:
    update_energy_status()
    if is_active:
        monte_carlo_step(current_monte_carlos_status)
    time.sleep(0.5)

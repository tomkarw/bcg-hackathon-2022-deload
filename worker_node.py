import json
import socketio
import time
import random
from energy_status import EnergyStatus
import logging
import os

from monte_carlo_status import MonteCarloStatus

try:
    from raspberry import act_compute_off, act_compute_on, update_energy_status
except ModuleNotFoundError:

    def act_compute_off():
        logging.info("COMPUTE OFF")

    def act_compute_on():
        logging.info("COMPUTE ON")

    def update_energy_status() -> EnergyStatus:
        return EnergyStatus(
            light=False,
            cpu_temperature=random.random(),
            environment_temperature=random.random(),
        )


## CONFIG ##
logging.basicConfig(level=logging.DEBUG)
sio = socketio.Client()

SERVER_URL = os.environ.get("SERVER_URL") or "http://localhost:8080"
DEBUG = os.environ.get("DEBUG") or True


is_active = False
compute_result = MonteCarloStatus(0, 0)

sio.connect(SERVER_URL)
logging.debug(f"{sio.sid=}")


@sio.on("compute_on")
def compute_on(data):
    global compute_result
    global is_active
    data = json.loads(data)
    compute_result = MonteCarloStatus(data["count_in"], data["count_out"])
    is_active = True
    act_compute_on()


@sio.on("compute_off")
def compute_off():
    global compute_result
    global is_active
    is_active = False
    send_result(compute_result)
    act_compute_off()


@sio.on("get_result")
def get_result():
    global compute_result
    send_result(compute_result)


def send_result(result: MonteCarloStatus):
    sio.emit("result", result.as_json())


@sio.on("*")
def catch_all(event, data):
    logging.debug("Received non-standard event")


while True:
    current_energy_status = update_energy_status()
    sio.emit("energy_status", current_energy_status.as_json())
    if is_active:
        compute_result.step()
        logging.info(f"PI={compute_result.approximation()}")
    time.sleep(0.5)

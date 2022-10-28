import json
import socketio
import time
import random
import logging
import os

from energy_status import EnergyStatus
from monte_carlo_status import MonteCarloStatus

try:
    from raspberry import act_compute_off, act_compute_on, update_energy_status
except ModuleNotFoundError:

    def act_compute_off():
        pass

    def act_compute_on():
        pass

    def update_energy_status() -> EnergyStatus:
        return EnergyStatus(
            light=False,
            cpu_temperature=random.random(),
            environment_temperature=random.random(),
        )


SERVER_URL = os.environ.get("SERVER_URL") or "http://localhost:8080"
DEBUG = os.environ.get("DEBUG") or True

## CLIENT
sio = socketio.Client()

## GLOBAL STATE
is_active = False
compute_result = MonteCarloStatus(0, 0)


@sio.on("compute_on")
def compute_on(data: str):
    logging.debug("COMPUTE ON")
    global compute_result
    global is_active
    compute_result = MonteCarloStatus.from_json(data)
    is_active = True
    act_compute_on()


@sio.on("compute_off")
def compute_off():
    logging.debug("COMPUTE OFF")
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


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.debug(f"STARTING NODE, id={sio.sid}")
    sio.connect(SERVER_URL)
    while True:
        logging.debug(f"WORKER LOOP, is_active={is_active}")
        current_energy_status = update_energy_status()
        sio.emit("energy_status", current_energy_status.as_json())
        if is_active:
            compute_result.step()
            logging.info(
                f"PI={compute_result.approximation()}, i={compute_result.count_in + compute_result.count_out}"
            )
        time.sleep(1)

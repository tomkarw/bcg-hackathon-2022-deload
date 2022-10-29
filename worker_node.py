import socketio
import time
import random
import logging
import os
import uuid

from node_status import NodeStatus
from monte_carlo_status import MonteCarloStatus

try:
    from raspberry import act_compute_off, act_compute_on, update_energy_status
except ModuleNotFoundError:

    def act_compute_off():
        pass

    def act_compute_on():
        pass

    def update_energy_status() -> NodeStatus:
        return NodeStatus(
            node_id=NODE_ID,
            light=False,
            cpu_temperature=random.random(),
            environment_temperature=random.random(),
        )


SERVER_URL = os.environ.get("SERVER_URL") or "http://localhost:8080"
DEBUG = os.environ.get("DEBUG") or True
NODE_ID = "NODE_" + hex(uuid.getnode())[2:]

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
    sio.connect(SERVER_URL)
    logging.debug(f"STARTING NODE, sid={sio.sid}")
    while True:
        logging.debug(f"WORKER LOOP, is_active={is_active}")
        current_energy_status = update_energy_status()
        print("WORKER LOOP after update_energy_status")
        sio.emit("energy_status", current_energy_status.as_json())
        print("WORKER LOOP after emit energy status")
        if is_active:
            print("WORKER LOOP is active")
            compute_result.step()
            print("WORKER LOOP after step")
            logging.info(
                f"PI={compute_result.approximation()}, i={compute_result.count_in + compute_result.count_out}"
            )
            send_result(compute_result)
            print("WORKER LOOP after send result")
        time.sleep(1)

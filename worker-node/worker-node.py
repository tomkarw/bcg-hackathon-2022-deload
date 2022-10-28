from dataclasses import asdict, dataclass
import socketio
import time
import random
import json

sio = socketio.Client()

SERVER_URL = "http://localhost:8080"
DEBUG = True


@sio.on("compute_on")
def on_message(data):
    status = MonteCarloStatus.fromJson(data)
    monte_carlo_step(data)
    sio.emit("result", data.asJson())


@sio.on("compute_off")
@sio.on("*")
def catch_all(event, data):
    print("Received non-standard event")


sio.connect(SERVER_URL)
print("my sid is", sio.sid)


def current_light_status():
    return random.random()


@dataclass
class MonteCarloStatus:
    count_in: int
    count_out: int

    def asJson(self):
        return json.dumps(asdict(self))


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


s = MonteCarloStatus(0, 0)

while True:
    sio.emit("light_status", {"light_status": current_light_status()})
    time.sleep(0.5)
    on_message(s)

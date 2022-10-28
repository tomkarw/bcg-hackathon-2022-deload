import socketio
import time

sio = socketio.Client()

SERVER_URL = "http://localhost:8080"


@sio.on("compute")
def on_message(data):
    print("I received a compute message!")


@sio.on("*")
def catch_all(event, data):
    print("Received non-standard event")


sio.connect(SERVER_URL)
print("my sid is", sio.sid)


def current_light_status():
    return 0


while true:
    sio.emit("light_status", {"light_status": current_light_status()})
    time.sleep(0.5)

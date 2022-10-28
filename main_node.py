from dataclasses import dataclass
from typing import List
from aiohttp import web
import socketio
from monte_carlo_status import MonteCarloStatus

## creates a new Async Socket IO Server
sio = socketio.AsyncServer()
## Creates a new Aiohttp Web Application
app = web.Application()
# Binds our Socket.IO server to our Web App
## instance
sio.attach(app)


@dataclass
class NodeState:
    energy_status: int = 0
    is_running: bool = False


nodes = {}


@sio.event
def connect(sid, environ, auth):
    print("connect ", sid)
    nodes[sid] = NodeState()
    print("nodes", nodes)
    print(nodes[sid].energy_status)


@sio.event
def disconnect(sid):
    print("disconnect ", sid)
    del nodes[sid]
    print("nodes", nodes)


@sio.on("energy_status")
async def on_message(unknown, sid: str, message):
    nodes[sid].energy_status = message["energy_status"]
    decide_which_node_should_run()


## choose node with best energy score
## if it's already computing, do nothing
## otherwise, find currently computing node and send compute_off event to it
def decide_which_node_should_run(nodes):
    best_node = choose_best_node(nodes)
    if nodes[best_node].is_running:
        return
    for id in nodes:
        if nodes[id].is_running:
            # send "compute off" message
            nodes[id].is_running = False
            sio.emit("compute_off", room=id)


def choose_best_node(nodes: List[dict]) -> str:
    return max(nodes, key=lambda node: node.energy_status)


@sio.on("result")
def result(unknown, sid: str, data: dict):
    result = MonteCarloStatus(data.count_in, data.count_off)
    best_node = choose_best_node(nodes)
    print(sid, result)
    sio.emit("compute_on", result, room=best_node)


## We kick off our server
if __name__ == "__main__":
    web.run_app(app)

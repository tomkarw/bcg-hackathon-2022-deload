from dataclasses import dataclass
import json
from typing import List, Optional
from aiohttp import web
import socketio
from energy_status import EnergyStatus
from monte_carlo_status import MonteCarloStatus
import logging
import os
import time


db_name = os.getenv("POSTGRES_DB")
db_user = os.getenv("POSTGRES_USER")
db_pass = os.getenv("POSTGRES_PASSWORD")
db_host = os.getenv("POSTGRES_HOST")

try:
    from dotenv import load_dotenv
    from postgres import Postgres

    load_dotenv()

    client = Postgres(
        "postgresql://%s:%s@%s:5432/%s" % (db_user, db_pass, db_host, db_name)
    )
except:
    logging.warning("Unable to connect to database, proceeds without database")
    client = None

logging.basicConfig(level=logging.DEBUG)

## creates a new Async Socket IO Server
sio = socketio.AsyncServer(cors_allowed_origins='*')
## Creates a new Aiohttp Web Application
app = web.Application()
# Binds our Socket.IO server to our Web App
## instance
sio.attach(app)


@dataclass
class NodeState:
    energy_status: int = 0


nodes = {}
current_working_node = None
current_monte_carlo_status = MonteCarloStatus(count_in=0, count_out=0)


@sio.event
async def connect(node_id, environ, auth):
    global current_working_node
    global current_monte_carlo_status
    global nodes
    logging.debug(f"connect node_id={node_id}")
    nodes[node_id] = NodeState()
    if current_working_node is None:
        current_working_node = node_id
        if not client is None:
            client.run(
                "INSERT INTO computes (node, compute) VALUES (%(node)s,1)",
                parameters={"node": current_working_node},
            )
        current_working_node = node_id
        await send_compute_on(node_id)


@sio.event
async def disconnect(node_id):
    global nodes
    global current_working_node
    logging.debug(f"disconnect {node_id}")
    del nodes[node_id]
    if node_id == current_working_node:
        await decide_which_node_should_run()


@sio.on("energy_status")
async def energy_status(sid: str, message: str):
    global nodes
    # logging.debug(f"{sid} {message}")
    energy_status = EnergyStatus.from_json(message)
    if not client is None:
        client.run(
            "INSERT INTO node_state (node, light, cpu_temp, env_temp) VALUES (%(node)s, %(light)s, %(cpu_temp)s, %(env_temp)s)",
            parameters={
                "node": sid,
                "light": int(energy_status.light),
                "cpu_temp": energy_status.cpu_temperature,
                "env_temp": energy_status.environment_temperature,
            },
        )
    nodes[sid].energy_status = energy_status.estimate()
    await decide_which_node_should_run()


## choose node with best energy score
## if it's already computing, do nothing
## otherwise, find currently computing node and send compute_off event to it
async def decide_which_node_should_run():
    global nodes
    global current_working_node
    best_node = choose_best_node(nodes)
    # logging.debug(f"{current_working_node} {best_node}")
    if best_node == current_working_node:
        return
    if current_working_node is None:
        return
    logging.debug(f"compute off, {current_working_node}")
    if not client is None:
        client.run(
            "INSERT INTO computes (node, compute) VALUES (%(node)s,0)",
            parameters={"node": current_working_node},
        )
    await sio.emit("compute_off", room=current_working_node)
    current_working_node = None


def choose_best_node(nodes: List[dict]) -> Optional[str]:
    return max(nodes, key=lambda node: nodes[node].energy_status) if nodes else None


@sio.on("result")
async def result(node_id: str, data: str):
    global current_working_node
    global current_monte_carlo_status
    current_monte_carlo_status = MonteCarloStatus.from_json(data)
    best_node = choose_best_node(nodes)
    current_working_node = best_node
    logging.debug(f"compute_on result, {best_node}")
    if not client is None:
        client.run(
            "INSERT INTO computes (node, compute) VALUES (%(node)s,1)",
            parameters={"node": current_working_node},
        )
    if current_working_node:
        await send_compute_on(best_node)


async def send_compute_on(node_id: str):
    global current_monte_carlo_status
    logging.debug(f"compute_on {current_monte_carlo_status}, {node_id}")
    await sio.emit("compute_on", current_monte_carlo_status.as_json(), room=node_id)


if __name__ == "__main__":
    web.run_app(app)

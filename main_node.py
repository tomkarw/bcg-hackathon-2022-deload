from dataclasses import dataclass
from typing import List, Optional
from aiohttp import web
import socketio
from node_status import NodeStatus
from monte_carlo_status import MonteCarloStatus
import logging
import os

logging.basicConfig(level=logging.DEBUG)

try:
    from dotenv import load_dotenv
    from postgres import Postgres

    load_dotenv()
    db_name = os.getenv("POSTGRES_DB")
    db_user = os.getenv("POSTGRES_USER")
    db_pass = os.getenv("POSTGRES_PASSWORD")
    db_host = os.getenv("POSTGRES_HOST")

    client = Postgres(
        "postgresql://%s:%s@%s:5432/%s" % (db_user, db_pass, db_host, db_name)
    )
except:
    logging.warning("Unable to connect to database, proceeds without database")
    client = None


## creates a new Async Socket IO Server
sio = socketio.AsyncServer(cors_allowed_origins="*")
## Creates a new Aiohttp Web Application
app = web.Application()
# Binds our Socket.IO server to our Web App
## instance
sio.attach(app)


@dataclass
class NodeState:
    node_id: str
    sid: str
    energy_status: int = 0


nodes = {}
current_working_node = None
current_monte_carlo_status = MonteCarloStatus(count_in=0, count_out=0)


@sio.event
async def connect(sid, environ, auth):
    global current_working_node
    global current_monte_carlo_status
    global nodes
    logging.debug(f"connect sid={sid}")


@sio.event
async def disconnect(sid: str):
    global nodes
    global current_working_node
    to_delete = None
    for node_id in nodes:
        if nodes[node_id].sid == sid:
            to_delete = node_id
    if to_delete:
        del nodes[to_delete]
    logging.debug(f"disconnect {to_delete}")
    if to_delete == current_working_node:
        await decide_which_node_should_run()


@sio.on("energy_status")
async def energy_status(sid: str, message: str):
    logging.debug(f"energy_status {message}")
    global nodes
    node_status = NodeStatus.from_json(message)
    if nodes.get(node_status.node_id) is None:
        nodes[node_status.node_id] = NodeState(sid=sid, node_id=node_status.node_id)
    if not client is None:
        client.run(
            "INSERT INTO node_state (node, light, cpu_temp, env_temp) VALUES (%(node)s, %(light)s, %(cpu_temp)s, %(env_temp)s)",
            parameters={
                "node": node_status.node_id,
                "light": int(node_status.light),
                "cpu_temp": node_status.cpu_temperature,
                "env_temp": node_status.environment_temperature,
            },
        )
    nodes[node_status.node_id].energy_status = node_status.estimate()
    await decide_which_node_should_run()


## choose node with best energy score
## if it's already computing, do nothing
## otherwise, find currently computing node and send compute_off event to it
async def decide_which_node_should_run():
    print("decide_which_node_should_run")
    logging.debug("decide_which_node_should_run")
    global nodes
    global current_working_node
    best_node = choose_best_node(nodes)
    # best node is already computing
    if best_node == current_working_node:
        logging.debug(f"best node already running: {best_node}")
        return
    # no node is computing
    if current_working_node is None:
        logging.debug(f"no node is computing yet, starting best node: {best_node}")
        current_working_node = nodes[best_node].node_id
        if not client is None:
            client.run(
                "INSERT INTO computes (node, compute) VALUES (%(node)s,1)",
                parameters={"node": current_working_node},
            )
        await send_compute_on(nodes[best_node].node_id)
        return
    # switch to best node
    logging.debug(f"compute off, {current_working_node}")
    if not client is None:
        client.run(
            # compute off
            "INSERT INTO computes (node, compute) VALUES (%(node)s,0)",
            parameters={"node": current_working_node},
        )
    await sio.emit("compute_off", room=current_working_node)
    current_working_node = None


def choose_best_node(nodes: List[dict]) -> Optional[str]:
    return max(nodes, key=lambda node: nodes[node].energy_status) if nodes else None


@sio.on("result")
async def result(sid: str, data: str):
    global current_working_node
    global current_monte_carlo_status
    current_monte_carlo_status = MonteCarloStatus.from_json(data)
    best_node = choose_best_node(nodes)
    current_working_node = best_node
    if current_working_node:
        logging.debug(f"compute_on {result}, {best_node}")
        if not client is None:
            client.run(
                # compute on
                "INSERT INTO computes (node, compute) VALUES (%(node)s,1)",
                parameters={"node": current_working_node},
            )
        await send_compute_on(best_node)


@sio.on("get_result")
async def get_result(sid: str):
    await sio.emit(
        "get_result_back", current_monte_carlo_status.approximation(), room=sid
    )
    return current_monte_carlo_status.approximation()


async def send_compute_on(node_id: str):
    global current_monte_carlo_status
    logging.debug(f"compute_on {current_monte_carlo_status}, {node_id}")
    await sio.emit(
        "compute_on", current_monte_carlo_status.as_json(), room=nodes[node_id].sid
    )


if __name__ == "__main__":
    web.run_app(app)

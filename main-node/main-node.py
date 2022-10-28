from dataclasses import dataclass
from aiohttp import web
import socketio
import json

## creates a new Async Socket IO Server
sio = socketio.AsyncServer()
## Creates a new Aiohttp Web Application
app = web.Application()
# Binds our Socket.IO server to our Web App
## instance
sio.attach(app)

# ## we can define aiohttp endpoints just as we normally
# ## would with no change
# async def index(request):
#     with open("index.html") as f:
#         return web

# ## We bind our aiohttp endpoint to our app
# ## router
# app.router.add_get("/", index).Response(text=f.read(), content_type="text/html")


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


@sio.on("*")
async def on_message(unknown, sid, message):
    nodes[sid].energy_status = message["light_status"]
    decide_which_node_should_run()


def decide_which_node_should_run():
    best_node = max(nodes, key=lambda node: node.energy_status)
    for id in nodes:
        if id == best_node:
            if not nodes[id].is_running:
                # send "compute on" message
                nodes[id].is_running = True
                sio.emit("compute_on", room=id)
        elif nodes[id].is_running:
            # send "compute off" message
            nodes[id].is_running = False
            sio.emit("compute_off", room=id)


## We kick off our server
if __name__ == "__main__":
    web.run_app(app)

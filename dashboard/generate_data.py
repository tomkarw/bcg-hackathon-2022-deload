import os
from dotenv import load_dotenv
from postgres import Postgres
import math
import time

load_dotenv()

db_name = os.getenv("POSTGRES_DB")
db_user = os.getenv("POSTGRES_USER")
db_pass = os.getenv("POSTGRES_PASSWORD")

client = Postgres("postgresql://%s:%s@localhost:5432/%s" % (db_user, db_pass, db_name))
res = client.all("SELECT * FROM cluster_state")
i = 0
while True:
    v = math.sin(i/10)*8+8
    time.sleep(0.5)
    client.run("INSERT INTO cluster_state (node, energy, load) VALUES (%(node)s, %(energy)s, %(load)s)",
    parameters={
        "node": "Node 1",
        "energy": v,
        "load": v
    })
    i += 1

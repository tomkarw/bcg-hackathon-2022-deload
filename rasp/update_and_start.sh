#!/bin/sh
# update_and_start.sh
# update deload and start it
cd /home/pi/
cd hackathon-2022/

SERVER_URL='http://18.185.215.55:8080' python -m worker_node > server.log

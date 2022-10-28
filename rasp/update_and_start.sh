#!/bin/sh
# update_and_start.sh
# update deload and start it
cd /home/pi/
rm -rf hackathon-2022-auto-update/
git clone https://github.com/tomkarw/hackathon-2022.git hackathon-2022-auto-update
cd hackathon-2022-auto-update/

cd hackathon-2022-auto-update/
SERVER_URL='http://18.185.215.55:8080' python -m worker_node > server.log

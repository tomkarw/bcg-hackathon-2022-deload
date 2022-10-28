#!/bin/sh
# update_and_start.sh
# update deload and start it
cd /home/pi/
git clone https://github.com/tomkarw/hackathon-2022.git hackathon-2022-auto-update
cd hackathon-2022-auto-update/worker-node/
python -m pip -r requirements.txt
python -m worker-node > server.log

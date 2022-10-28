#!/bin/sh
# update_and_start.sh
# update deload and start it
cd /home/pi/
git clone https://github.com/tomkarw/hackathon-2022.git
cd hackathon-2022/worker-node/
python -m pip -r requirements.txt
python -m worker-node > server.log

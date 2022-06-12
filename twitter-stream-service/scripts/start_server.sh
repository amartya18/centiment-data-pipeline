#!/bin/bash
cd /home/ec2-user/twitter-stream-service
~/.nvm/versions/node/v16.15.1/bin/pm2 start main.py --name twitter-stream-service

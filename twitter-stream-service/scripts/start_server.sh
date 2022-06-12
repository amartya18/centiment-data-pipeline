#!/bin/bash
pwd
~/.nvm/versions/node/v16.15.1/bin/pm2 status
~/.nvm/versions/node/v16.15.1/bin/pm2 start /home/ec2-user/twitter-stream-service/main.py --name twitter-stream-service

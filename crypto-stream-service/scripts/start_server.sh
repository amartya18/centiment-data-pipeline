#!/bin/bash
/usr/bin/pm2 start /home/ec2-user/crypto-stream-service/main.py --name crypto-stream-service --interpreter /home/ec2-user/crypto-stream-service/environment/bin/python --no-autorestart

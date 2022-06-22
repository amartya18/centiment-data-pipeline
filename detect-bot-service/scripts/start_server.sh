#!/bin/bash
/usr/bin/pm2 start /home/ec2-user/detect-bot-service/main.py --name detect-bot-service --interpreter /home/ec2-user/detect-bot-service/environment/bin/python --no-autorestart

#!/bin/bash
/usr/bin/pm2 start /home/ec2-user/data-transformation-service/ohlc.py --name ohlc-data-transformation-service --interpreter /home/ec2-user/data-transformation-service/environment/bin/python --no-autorestart
# /usr/bin/pm2 start /home/ec2-user/data-transformation-service/main.py --name data-transformation-service --interpreter /home/ec2-user/data-transformation-service/environment/bin/python --no-autorestart

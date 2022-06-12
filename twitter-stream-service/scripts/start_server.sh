#!/bin/bash
/usr/bin/pm2 start /home/ec2-user/twitter-stream-service/main.py --name twitter-stream-service --interpreter /home/ec2-user/twitter-stream-service/environment/bin/python

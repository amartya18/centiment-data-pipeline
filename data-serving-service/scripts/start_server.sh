#!/bin/bash
/usr/bin/pm2 start "/home/ec2-user/data-serving-service/environment/bin/uvicorn main:app --host 0.0.0.0 --port 5001" --name data-serving-service --interpreter /home/ec2-user/data-serving-service/environment/bin/python --no-autorestart

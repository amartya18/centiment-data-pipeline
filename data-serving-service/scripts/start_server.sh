#!/bin/bash
/usr/bin/pm2 start "/home/ec2-user/data-serving-service/environment/bin/gunicorn main:app --workers 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:5001" --name data-serving-service
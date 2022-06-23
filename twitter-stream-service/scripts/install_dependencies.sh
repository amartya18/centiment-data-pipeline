#!/bin/bash
echo Deleting existing python venv 
sudo rm -rf /home/ec2-user/twitter-stream-service/environment

echo Creatuing new python venv 
sudo python3 -m venv /home/ec2-user/twitter-stream-service/environment

echo Installing python packages 
sudo /home/ec2-user/twitter-stream-service/environment/bin/pip install -r /home/ec2-user/twitter-stream-service/requirements.txt

#!/bin/bash
echo Deleting existing python venv 
sudo rm -rf /home/ec2-user/data-serving-service/environment

echo Creating new python venv 
sudo python3.8 -m venv /home/ec2-user/data-serving-service/environment

echo Installing python packages 
sudo /home/ec2-user/data-serving-service/environment/bin/pip install -r /home/ec2-user/data-serving-service/requirements.txt

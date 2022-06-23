#!/bin/bash
echo Deleting existing python venv 
sudo rm -rf /home/ec2-user/detect-bot-service/environment

echo Creatuing new python venv 
sudo python3.8 -m venv /home/ec2-user/detect-bot-service/environment
source /home/ec2-user/detect-bot-service/environment/bin/activate

echo Installing python packages 
sudo /home/ec2-user/detect-bot-service/environment/bin/pip install -r /home/ec2-user/detect-bot-service/requirements.txt

deactivate
#!/bin/bash
curl -O https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py --user

echo Installing python packages in: $PWD

pip install -r requirements.txt

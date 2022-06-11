#!/bin/bash
function program_is_installed {
  local return_=1
  type $1 >/dev/null 2>&1 || { local return_=0; }
  echo "$return_"
}

if [ $(program_is_installed pip) = 1 ] ; then
    echo "pip installed already..."
else
    echo "pip not installed yet.."
    curl -O https://bootstrap.pypa.io/get-pip.py
    python3 get-pip.py --user
fi

if [ $(program_is_installed npm) = 1 ] ; then
    echo "npm installed already..."
else
    echo "npm not installed yet.."
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
    . ~/.nvm/nvm.sh
    nvm install node
    npm install pm2@latest -g
fi

echo Installing python packages in: $PWD
pip install -r requirements.txt

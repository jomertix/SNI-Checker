#!/bin/bash

sudo apt update
sudo apt install git pip -y
git clone https://github.com/jomertix/SNI-checker.git
cd SNI-Checker
pip install -r requirements.txt
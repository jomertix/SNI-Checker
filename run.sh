#!/bin/bash

sudo apt update
sudo apt install git pip -y
git clone https://github.com/jomertix/SNI-Checker.git
(cd SNI-Checker && pip install -r requirements.txt -q --exists-action i)

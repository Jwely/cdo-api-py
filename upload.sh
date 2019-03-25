#!/usr/bin/env bash
sudo apt-get install twine
twine upload dist/*
sudo rm -rf build
sudo rm -rf dist
sudo rm -rf cdo_api_py.egg-info
sudo -H pip3 install --upgrade cdo-api-py

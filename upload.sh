#!/usr/bin/env bash
twine upload dist/*
rm -rf build
rm -rf dist
rm -rf cdo_api_py.egg-info
sudo pip3 install --upgrade cdo-api-py
sudo pip install --upgrade cdo-api-py

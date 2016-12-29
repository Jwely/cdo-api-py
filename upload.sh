#!/usr/bin/env bash
twine upload dist/*
rm -rf build
rm -rf dist
rm -rf cdo_api_client.egg-info
sudo pip3 install --upgrade cdo-api-client
sudo pip install --upgrade cdo-api-client

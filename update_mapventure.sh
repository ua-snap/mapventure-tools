#! /bin/bash

export GEONODE_URL="http://mapventure.iarc.uaf.edu:8000"
export GEOSERVER_URL="http://mapventure.iarc.uaf.edu:8080/geoserver"
export MV_LEAFLET_IMAGE_PATH="images/"
BRANCH_NAME=$1

git clone -b $BRANCH_NAME https://github.com/ua-snap/mapventure.git && cd mapventure

npm install && grunt build --dist

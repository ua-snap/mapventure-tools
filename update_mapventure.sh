#! /bin/bash

export GEONODE_URL="http://mapventure.iarc.uaf.edu:8000"
export GEOSERVER_URL="http://mapventure.iarc.uaf.edu:8080/geoserver"
export MV_LEAFLET_IMAGE_PATH="bower_components/leaflet/dist/images/"
export MAPVENTURE_DIST="/var/www/mapventure-dist"

BRANCH_NAME=$1
BUILD_DIR="/tmp"

if [ -z $BRANCH_NAME ]
	then
		echo "Branch name not specified, exiting."
		exit 1
fi

cd $BUILD_DIR

if [ ! -d mapventure ]
	then
		git clone https://github.com/ua-snap/mapventure.git
fi

cd mapventure
git pull
git checkout $BRANCH_NAME

npm install && grunt build --dist

sudo rm -rf /tmp/mapventure-dist && sudo mv $MAPVENTURE_DIST /tmp/mapventure-dist && sudo cp -r dist $MAPVENTURE_DIST && sudo chown -R www-data:www-data $MAPVENTURE_DIST && sudo ln -s /var/www/downloads /var/www/mapventure-dist/downloads

sudo service apache2 restart

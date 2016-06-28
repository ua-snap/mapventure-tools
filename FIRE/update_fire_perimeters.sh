#! /bin/bash
# This script updates the Active Fires layer for the current year.

if [ -z "$GEONODE_VIRTUALENV_PATH" ] \
	|| [ -z "$GEONODE_INSTALL_PATH" ] \
	|| [ -z "$FIREVENTURE_VIRTUALENV_PATH" ] \
	|| [ -z "$FIREVENTURE_PATH" ] \
	|| [ -z "$DATA_WORKING_DIRECTORY" ]; then

	cat <<ERROR_MSG
Some required environment variables are missing:

GEONODE_VIRTUALENV_PATH=[$GEONODE_VIRTUALENV_PATH]
GEONODE_INSTALL_PATH=[$GEONODE_INSTALL_PATH]
FIREVENTURE_VIRTUALENV_PATH=[$FIREVENTURE_VIRTUALENV_PATH]
FIREVENTURE_PATH=[$FIREVENTURE_PATH]
DATA_WORKING_DIRECTORY=[$DATA_WORKING_DIRECTORY]

ERROR_MSG
	exit 1

fi

# Configure geonode's virtual environment
# export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python
# export WORKON_HOME="/home/$prefix/.venvs"

# Set the import date and current year.
import_date="`date +'%Y-%m-%d %H:%M:%S'`"

# This will automatically collect the current date's
# fire perimeters and update the request from the ArcGIS server based on the current year.
source $FIREVENTURE_VIRTUALENV_PATH/bin/activate
`which python` $FIREVENTURE_PATH/fetch_fire_perimeters.py -p $DATA_WORKING_DIRECTORY

# Import the current layer with the current updated date. Has a high verbosity of reporting to let
# us be aware of any issues taking place.
source $GEONODE_VIRTUALENV_PATH/bin/activate
`which python` $GEONODE_INSTALL_PATH/geonode/manage.py importlayers -v 3 -d "$import_date" -t "Active Fires" -o $DATA_WORKING_DIRECTORY/fireperimeters_2016_all_cleaned_joined.shp

# Remove the current date's active fire perimeter files.
rm -f $DATA_WORKING_DIRECTORY/fire*

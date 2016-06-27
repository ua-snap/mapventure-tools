#! /bin/bash
# This script updates the Active Fires layer for the current year.
# Maintainer: Bob Torgerson - SNAP (Scenarios Network of Alaska & Arctic Planning)

# If this is running on a local dev VM, we need
# some prefixes
if [ -z "$MV_LOCAL" ]; then
  # Non-local env
  echo "Running in production environment..."
  prefix='geonode'
  export INSTALL_DIR=/home/geonode/
else
  echo "Running in dev VM environment..."
  export INSTALL_DIR=/install/portal/
  prefix=''
fi

# Configure geonode's virtual environment
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python
export WORKON_HOME="/home/$prefix/.venvs"

source "$WORKON_HOME/geonode/bin/activate"

# Set the import date and current year. This will automatically collect the current date's
# fire perimeters and update the request from the ArcGIS server based on the current year.
import_date="`date +'%Y-%m-%d %H:%M:%S'`"

`which python` $INSTALL_DIR/mapventure-tools/FIRE/get_fire_data.py -p $INSTALL_DIR/mapventure-tools/FIRE/fire-updates/

# Import the current layer with the current updated date. Has a high verbosity of reporting to let
# us be aware of any issues taking place.
`which python` $INSTALL_DIR/geonode/manage.py importlayers -v 3 -d "$import_date" -t "Active Fires" -o $INSTALL_DIR/mapventure-tools/FIRE/fire-updates/fireperimeters_2016_all_cleaned_joined.shp

# Remove the current date's active fire perimeter files.
rm -f $INSTALL_DIR/mapventure-tools/FIRE/fire-updates/fire*

# Overview

This code combines data from different endpoints to make a single shapefile of active fire perimeters in Alaska.

The Python code does the geospatial lifting, and the shell script is for automation on the production server.

# Installation

GDAL >1.11 must be available on the system.

Installing the Python module needs a bit of work done prior to ensure some dependencies (Debian/Ubuntu) are met.  First prepare some dependencies and a `virtualenv`:

```
cd /path/to/some/folder/
virtualenv fireventure-virtualenv
source fireventure-virtualenv/bin/activate
cd /path/to/mapventure-tools/FIRE
pip install -e .
```

To run the `update_fire_perimeters.sh` script, several environment variables must be set, here are examples that indicate the right endpoints (will vary depending on system):

```
export GEONODE_VIRTUALENV_PATH=/home/vagrant/.venvs
export GEONODE_INSTALL_PATH=/install/portal
export FIREVENTURE_VIRTUALENV_PATH=/home/vagrant/fireventure
export FIREVENTURE_PATH=/install/FIRE
export DATA_WORKING_DIRECTORY=/tmp
```

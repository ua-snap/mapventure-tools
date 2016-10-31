#!/usr/bin/python
import urllib2
import os
import subprocess
import json
import re
import sys
import logging
from datetime import datetime, timedelta

logging.basicConfig(format = '%(levelname)s: %(message)s', level = logging.DEBUG)

geonodePath = os.environ['GEONODE_INSTALL_PATH']
geonodeVenv = os.environ['GEONODE_VIRTUALENV_PATH']
workingDir = os.environ['DATA_WORKING_DIRECTORY']

jsonFeed = 'http://feeder.gina.alaska.edu/radar-uaf-barrow-seaice-geotif.json'

# Number of layers to import into GeoNode.
maxLayers = 3

# Target time interval between GeoNode layers.
layerInterval = timedelta(minutes=30)

# How recent does the first GeoTIFF need to be?
offsetFromNow = timedelta(minutes=10)

# Acceptable time buffer before and after target time.
acceptableRange = timedelta(minutes=3)

# Download and parse GINA's Barrow sea ice GeoTIFF feed.
# The first element in the feed is the most recent GeoTIFF.
response = urllib2.urlopen(jsonFeed)
geoTiffs = json.loads(response.read())

# Create a datetime object from a date string from the GeoTIFF feed.
def dateObject(rawDate):
    # Grab the latest GeoTIFF's creation date, throwing out the time zone
    # because strptime() is not able to parse the time zone in this format.
    match = re.search('^.*(?=-0[8-9]:00$)', rawDate)
    return datetime.strptime(match.group(0), '%Y-%m-%dT%H:%M:%S')

# Format the date as needed for GeoNode's importlayers management command.
def formatDate(dateObj):
    return dateObj.strftime('%Y-%m-%d %H:%M:%S')

# Download and save the GeoTIFF file.
def download(geoTiffUrl):
    rawGeoTiff = workingDir + '/barrow_raw.tif'
    response = urllib2.urlopen(geoTiffUrl)
    localFile = open(rawGeoTiff, 'wb')
    localFile.write(response.read())
    localFile.close()
    return rawGeoTiff

# Georeference the GeoTIFF in EPSG:3857 and make the background transparent.
def process(rawGeoTiff):
    processedGeoTiff = workingDir + '/barrow_sea_ice_radar.tif'

    devnull = open(os.devnull, 'w')
    subprocess.call([
      'gdalwarp',
      '-s_srs',
      '+proj=aeqd +lat_0=71.2925 +lon_0=-156.788333333333 +x_0=0 +y_0=0 +a=6358944.3 +b=6358944.3 +units=m +no_defs',
      '-t_srs',
      'EPSG:3857',
      '-of',
      'GTiff',
      '-srcnodata',
      '0',
      '-dstalpha',
      rawGeoTiff,
      processedGeoTiff
    ], stdout=devnull, stderr=devnull)

    return processedGeoTiff

# Import the GeoTIFF over the existing Barrow sea ice layer in GeoNode, and
# update its publication date with the GeoTIFF's creation date.
def importLayer(processedGeoTiff, formattedDate, sequenceNumber):
    geonodeVenvPython = geonodeVenv + '/bin/python'

    devnull = open(os.devnull, 'w')
    subprocess.call([
      geonodeVenvPython,
      geonodePath + '/geonode/manage.py',
      'importlayers',
      '-d',
      formattedDate,
      '-t',
      'Barrow sea ice radar ' + str(sequenceNumber),
      '-o',
      processedGeoTiff
    ], stdout=devnull, stderr=devnull)

# Date of the first (most recent) layer in the GeoJSON feed.
firstDate = dateObject(geoTiffs[0]['event_at'])

if(firstDate < datetime.now() - offsetFromNow):
    logging.error("Date of first GeoTIFF is not recent enough.")
    sys.exit()

# Last possible date we are interested in.
lastDate = firstDate - layerInterval * maxLayers

# Use these to strictly enforce the position of our layers in GeoNode.
targetPosition = 0
success = {}

for sourcePosition in range(0, len(geoTiffs)):
    if(targetPosition == maxLayers):
        sys.exit()

    geoTiff = geoTiffs[sourcePosition]
    currentDate = dateObject(geoTiff['event_at'])

    # Compute the expected date and an acceptable time buffer on either side.
    expectedDate = firstDate - layerInterval * targetPosition
    lowEnd = expectedDate - acceptableRange
    highEnd = expectedDate + acceptableRange

    if(currentDate > lowEnd and currentDate < highEnd):
        # Process the GeoTIFF's date and raster data, then import into GeoNode.
        formattedDate = formatDate(currentDate)
        rawGeoTiff = download(geoTiff['source'])
        processedGeoTiff = process(rawGeoTiff)
        importLayer(processedGeoTiff, formattedDate, targetPosition + 1)

        # Clean up temporary files to avoid future GDAL warnings.
        os.remove(rawGeoTiff)
        os.remove(processedGeoTiff)

        logging.info("Successfully imported GeoNode layer {0} with date {1}.".format(targetPosition + 1, formattedDate))

        # Mark this GeoNode target layer as a success and move on.
        success[targetPosition] = True
        targetPosition += 1
    elif(currentDate < lowEnd and targetPosition not in success):
        # There are no more chances to find a suitable layer for this GeoNode
        # target layer. Mark it as a failure and move on.
        # TODO: Disable or delete failed layers from GeoNode to avoid confusion.

        logging.info("Failed to import GeoNode layer {0}.".format(targetPosition + 1))

        success[targetPosition] = False
        targetPosition += 1
    elif(currentDate < lastDate):
        sys.exit()

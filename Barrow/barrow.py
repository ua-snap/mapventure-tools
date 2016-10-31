#!/usr/bin/python
import urllib2
import os
import subprocess
import json
import re
from datetime import datetime

geonodePath = os.environ['GEONODE_INSTALL_PATH']
geonodeVenv = os.environ['GEONODE_VIRTUALENV_PATH']
workingDir = os.environ['DATA_WORKING_DIRECTORY']
jsonFeed = 'http://feeder.gina.alaska.edu/radar-uaf-barrow-seaice-geotif.json'

# Download and parse GINA's Barrow sea ice GeoTIFF feed.
# The first element in the feed is the most recent GeoTIFF.
response = urllib2.urlopen(jsonFeed)
geoTiffs = json.loads(response.read())

# Format the date as needed for GeoNode's importlayers management command.
def formatDate(geoTiffDate):
    # Grab the latest GeoTIFF's creation date, throwing out the time zone because
    # strptime() is not able to parse the time zone in this format.
    match = re.search('^.*(?=-0[8-9]:00$)', geoTiffDate)
    dateObject = datetime.strptime(match.group(0), '%Y-%m-%dT%H:%M:%S')

    return dateObject.strftime('%Y-%m-%d %H:%M:%S')

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
    ])

    return processedGeoTiff

# Import the GeoTIFF over the existing Barrow sea ice layer in GeoNode, and
# update its publication date with the GeoTIFF's creation date.
def importLayer(processedGeoTiff, formattedDate, sequenceNumber):
    geonodeVenvPython = geonodeVenv + '/bin/python'

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
    ])

for i in range(0, 3):
    geoTiff = geoTiffs[i]

    formattedDate = formatDate(geoTiff['event_at'])
    rawGeoTiff = download(geoTiff['source'])
    processedGeoTiff = process(rawGeoTiff)
    importLayer(processedGeoTiff, formattedDate, i + 1)

    # Clean up temporary files so we don't get warnings from GDAL in the future.
    os.remove(rawGeoTiff)
    os.remove(processedGeoTiff)

# WSGI module for use with Apache mod_wsgi or gunicorn

# # uncomment the following lines for logging
# # create a log.ini with `mapproxy-util create -t log-ini`
# from logging.config import fileConfig
# import os.path
# fileConfig(r'/home/geonode/mapventure-mapproxy/log.ini', {'here': os.path.dirname(__file__)})

from mapproxy.wsgiapp import make_wsgi_app
# Change this to match the server running MapProxy
application = make_wsgi_app('/home/osm/mapventure-tools/MapProxy/mapproxy.yaml')

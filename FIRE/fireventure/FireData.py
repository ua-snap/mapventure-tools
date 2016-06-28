# GET FIRE DATA FROM AICC ALASKA FIRE REST SERVICES
import requests

class FireData( object ):
    def __init__( self, baseurl, *args, **kwargs ):
        '''
        return fire data from ESRI REST services at AICC

        ARGUMENTS:
        ----------
        baseurl = [str] url to the base ESRI REST service.

        ** for AICC holdings an example is as follows:
        'http://afs.ak.blm.gov/arcgis/rest/services/MapAndFeatureServices/\n
                    CurrentFiresService/MapServer'
        RETURNS:
        --------
        object of type FireData containing the following attributes:
        [ baseurl, layers, queryurl, dat, fields, meta, json ]

        '''
        self.baseurl = baseurl
        self.layers = self._discover_layers()
        self.queryurl = None
        self.dat = None
        self.fields = None
        self.meta = None
        self.json = None

    def _discover_layers( self ):
        '''
        return a dict of the available layers and their identifiers.
        this is useful for the discovery of what layer id's to use in
        FireData.get_data( )
        '''
        r = requests.get( self.baseurl + '/'+ 'layers', params={'f':'pjson'} )
        return { i['id']:i['name'] for i in r.json()[ 'layers' ] }

    def get_meta( self, layerid=0, params={'f':'pjson'} ):
        '''
        return layer metadata including FIELDS which is useful for
        crafting the `outFields` {'key':'value'} pair which will tell
        the service what fields to return. There can be an abundance.

        ARGUMENTS:
        ----------
        layerid = [int] id of the layer to select from. default:0
        params = [dict] default:{'f':'pjson'} which tells to
                    return as json.

        RETURNS:
        --------
        self.meta and self.fields, where self.meta has all metadata as json
        about the layer being queried and self.fields containing a list of dicts
        containing attributes of the fields.

        '''
        path = '/'.join([ self.baseurl, str( layerid ) ])
        r = requests.get( path,  params=params )
        self.meta = r.json()
        self.fields = r.json()[ 'fields' ]

    def get_data( self, layerid=0, params={'where':''}, crs=3572 ):
        '''
        make a request to the AICC REST services with a query dict of
        {key:value} pairs of search parameters.

        ARGUMENTS:
        ----------
        layerid = [int] id of the layer to select from
        params = [dict] dict of {'key':'value'} pairs of search parameters
                    to pass to the REST service.
        crs = [int] EPSG code for the reference system to return the data in.

        RETURNS:
        --------
        self.dat & self.json where .dat is the returned `requests` get object
        and .json is the dat.json() helper.

        '''
        path = '/'.join([ self.baseurl, str( layerid ), 'query' ])
        r = requests.get( path, params=params )
        self.dat = r
        self.json = self.dat.json()
